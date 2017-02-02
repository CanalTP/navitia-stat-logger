import logging
from logging.config import dictConfig
import stat_logger.stat_pb2
from google.protobuf.message import DecodeError
import json
from protobuf_to_dict import protobuf_to_dict
import kombu
from kombu.mixins import ConsumerMixin
from datetime import datetime
from pywebhdfs.webhdfs import PyWebHdfsClient
import os
import platform


class Daemon(ConsumerMixin):
    def __init__(self, config):
        self.connection = None
        self.queues = []
        self.config = config
        logging.config.dictConfig(config['logger'])
        self._init_rabbitmq()
        if self.config['storage']['localfs']:
            self.logfile = None
            self.current_logfile_path=''
        # Initialize WebHDFS client
        if self.config['storage']['hdfs']:
            self.hdfs = PyWebHdfsClient(host=config['webhdfs']['host'], port=config['webhdfs']['port'], timeout=config['webhdfs']['timeout'])
            self.filename_template = config['webhdfs']['filename_template']

    def _init_rabbitmq(self):
        """
        connect to rabbitmq and init the queues
        """
        self.connection = kombu.Connection(self.config['rabbitmq']['broker-url'])
        exchange_name = self.config['rabbitmq']['exchange-name']
        exchange = kombu.Exchange(exchange_name, type="topic")
        logging.getLogger('stat_logger').info("listen exchange {0:s} on {1:s}".format(exchange_name, self.config['rabbitmq']['broker-url']))

        queue = kombu.Queue(exchange=exchange, durable=False, auto_delete=True, routing_key="#")
        self.queues.append(queue)
        
    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=self.queues, callbacks=[self.process_task])]

    def process_task(self, body, message):
        stat_request = stat_logger.stat_pb2.StatRequest()
        try:
            stat_request.ParseFromString(body)
            logging.getLogger('stat_logger').debug('query received: {}'.format(str(stat_request)))
        except DecodeError as e:
            logging.getLogger('stat_logger').warn("message is not a valid "
                "protobuf task: {}".format(str(e)))
            message.ack()
            return

        self.log_message(stat_request)
        message.ack()

    def log_message(self, stat_hit):
        if stat_hit.IsInitialized():
            content = json.dumps(protobuf_to_dict(stat_hit), separators=(',', ':')) + '\n'

            if self.config['storage']['localfs']:
                self._reopen_logfile(datetime.utcfromtimestamp(stat_hit.request_date))
                self.logfile.write(content)
                self.logfile.flush()

            if self.config['storage']['hdfs']:
                target_filename = self.filename_template.replace('{request_date}', datetime.utcfromtimestamp(stat_hit.request_date).strftime('%Y%m%d'))
                try:
                    self.hdfs.append_file(target_filename, content)
                except Exception as e:
                    print e

    def _reopen_logfile(self, log_date):
        expected_logfile_path = self._get_logfile_path(log_date)
        if self.current_logfile_path != expected_logfile_path:
            if self.logfile is not None:
                self.logfile.close()
            print "Opening file " + expected_logfile_path
            expected_log_dir = os.path.dirname(expected_logfile_path)
            if not os.path.isdir(expected_log_dir):
                os.makedirs(expected_log_dir)
            self.logfile = open(expected_logfile_path, 'a')
            self.current_logfile_path = expected_logfile_path

    def _get_logfile_path(self, log_date):
        return self.config['localfs']['root_dir'] + '/' + log_date.strftime('%Y/%m/%d') + '/stat_log_prod_' + log_date.strftime('%Y%m%d') + '_' + platform.node() + '_' + str(os.getpid()) + '.json.log'

    def __del__(self):
        self.close()

    def close(self):
        if self.logfile is not None:
            self.logfile.close()
        if self.connection and self.connection.connected:
            self.connection.release()
