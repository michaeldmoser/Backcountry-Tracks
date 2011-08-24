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
        logging.debug('Received request for gear list: %s' % data)
        request = json.loads(data)
        user = request['params'][0]

        properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = header.correlation_id
                )
        gear_list = self.geardb.list(user)
        logging.debug('Gear list is:\n%s' % gear_list)
        logging.debug('Publish response to %s to routing key %s' % (header.correlation_id, header.reply_to))
        self.channel.basic_publish(
                exchange = 'rpc_reply',
                routing_key = header.reply_to,
                properties = properties,
                body = json.dumps(gear_list)
                )



