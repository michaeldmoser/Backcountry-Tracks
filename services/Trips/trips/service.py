import pika
import json

import logging

class TripsService(object):

    def __init__(self, channel, configuration, db):
        self.channel = channel
        self.config = configuration
        self.db = db

    def start(self):
        rpc_queue = self.config['queues']['rpc']

        logging.debug("My Configuration: %s" % self.config)
        self.channel.basic_consume(self.process_request, queue=rpc_queue)

    def process_request(self, channel, method, header, data):
        request = json.loads(data)

        properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = header.correlation_id
                )

        logging.info('Received %s request' % request['method'])
        method = getattr(self.db, request['method'])
        response = method(*request['params'])

        if response is None:
            return

        logging.debug('Publish response to %s to routing key %s' % (header.correlation_id, header.reply_to))
        self.channel.basic_publish(
                exchange = 'rpc_reply',
                routing_key = header.reply_to,
                properties = properties,
                body = json.dumps(response)
                )



