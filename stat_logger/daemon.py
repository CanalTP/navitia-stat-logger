import logging
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
import gzip

import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter

class Daemon(ConsumerMixin):
    def __init__(self, config):
        self.connection = None
        self.queues = []
        self.config = config
        self._init_rabbitmq()
        if self.config['storage']['localfs']:
            self.logfile = None
            self.current_logfile_path=''
        # Initialize WebHDFS client
        if self.config['storage']['hdfs']:
            self.hdfs = PyWebHdfsClient(host=config['webhdfs']['host'], port=config['webhdfs']['port'], timeout=config['webhdfs']['timeout'])
            self.filename_template = config['webhdfs']['filename_template']
        self.schema = avro.schema.parse(open("stat.avsc").read())
        self.treated_items = 0

    def _init_rabbitmq(self):
        """
        connect to rabbitmq and init the queues
        """
        self.connection = kombu.Connection(self.config['rabbitmq']['broker-url'])
        exchange_name = self.config['rabbitmq']['exchange-name']
        exchange = kombu.Exchange(exchange_name, type="direct")
        logging.getLogger('stat_logger').info("listen following exchange: %s", exchange_name)
        print ("listen following exchange: {}".format(exchange_name))

        queue = kombu.Queue(exchange=exchange, durable=False, auto_delete=True)
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
        self.treated_items += 1
        if self.treated_items % 100 == 0:
            print "Checkpoint: Treated items = " + str(self.treated_items)

    def log_message(self, stat_hit):
        if stat_hit.IsInitialized():
            contentDict = protobuf_to_dict(stat_hit)
            content = json.dumps(contentDict, separators=(',', ':')) + '\n'

            if self.config['storage']['localfs']:
                self._reopen_logfile(datetime.utcfromtimestamp(stat_hit.request_date))
                # self.logfile.write(content)
                self.logfile.append(contentDict)
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
            if not os.path.exists(expected_logfile_path):
                self.logfile = DataFileWriter(open(expected_logfile_path, 'wb'), DatumWriter(), self.schema, codec='deflate')
            else:
                self.logfile = DataFileWriter(open(expected_logfile_path, 'ab+'), DatumWriter())
            self.current_logfile_path = expected_logfile_path

    def _get_logfile_path(self, log_date):
        return self.config['localfs']['root_dir'] + '/' + log_date.strftime('%Y/%m/%d') + '/stat_log_prod_' + log_date.strftime('%Y%m%d') + '_' + platform.node() + '_' + str(os.getpid()) + '.avro'

    def __del__(self):
        self.close()

    def close(self):
        if self.logfile is not None:
            self.logfile.close()
        if self.connection and self.connection.connected:
            self.connection.release()
