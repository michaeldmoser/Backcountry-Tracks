import pika
import json

from gear.usergear import UserGear

import logging

class GearService(object):

    def __init__(self, channel, configuration, geardb):
        self.channel = channel
        self.config = configuration
        self.geardb = geardb

    def start(self):
        user_gear_queue = self.config['queues']['user_gear']

        logging.debug("My Configuration: %s" % self.config)
        self.channel.basic_consume(self.process_request, queue=user_gear_queue)

    def process_request(self, channel, method, header, data):
        request = json.loads(data)

        properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = header.correlation_id
                )

        logging.info('Received %s request' % request['method'])
        method = getattr(self.geardb, request['method'])
        response = method(*request['params'])

        logging.debug('Publish response to %s to routing key %s' % (header.correlation_id, header.reply_to))
        self.channel.basic_publish(
                exchange = 'rpc_reply',
                routing_key = header.reply_to,
                properties = properties,
                body = json.dumps(response)
                )



