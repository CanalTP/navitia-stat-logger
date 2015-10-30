import logging
import stat_logger.stat_pb2
from google.protobuf.message import DecodeError
import json
from protobuf_to_dict import protobuf_to_dict
import kombu
from kombu.mixins import ConsumerMixin
from datetime import datetime
from pywebhdfs.webhdfs import PyWebHdfsClient


class Daemon(ConsumerMixin):
    def __init__(self, config):
        self.connection = None
        self.queues = []
        self.config = config
        self._init_rabbitmq()
        if self.config['storage']['localfs']:
            self.logfile = open('/tmp/stat_log_prod_' + datetime.utcnow().strftime('%Y%m%d_%H%M%S') + '.json.log', 'a')
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

    def log_message(self, stat_hit):
        if stat_hit.IsInitialized():
            content = json.dumps(protobuf_to_dict(stat_hit), separators=(',', ':')) + '\n'

            if self.config['storage']['localfs']:
                self.logfile.write(content)
                self.logfile.flush()

            if self.config['storage']['hdfs']:
                target_filename = self.filename_template.replace('{request_date}', datetime.utcfromtimestamp(stat_hit.request_date).strftime('%Y%m%d'))
                print target_filename
                try:
                    self.hdfs.append_file(target_filename, content)
                except Exception as e:
                    print e

    def __del__(self):
        self.close()

    def close(self):
        self.logfile.close()
        if self.connection and self.connection.connected:
            self.connection.release()
