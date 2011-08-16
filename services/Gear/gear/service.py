import pika
import json

from gear.usergear import UserGear

class GearService(object):

    def __init__(self, channel, configuration, geardb):
        self.channel = channel
        self.config = configuration
        self.geardb = geardb

    def start(self):
        user_gear_queue = self.config['queues']['user_gear']

        self.channel.basic_consume(self.process_request, queue=user_gear_queue)

    def process_request(self, channel, method, header, data):
        request = json.loads(data)
        user = request['params'][0]

        properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = header.correlation_id
                )
        gear_list = self.geardb.list(user)
        self.channel.basic_publish(
                exchange = 'rpc_reply',
                routing_key = header.reply_to,
                properties = properties,
                body = json.dumps(gear_list)
                )



