from tornado import web
import pika

import uuid
import json

# FIXME: Remove this thing
fake_gear_list = [
            {
            'name': 'Backpack',
            'description': 'Something you wear on your back to carry your gear',
            'weight': '48 oz'
            },
            {
            'name': 'Backpacking Stove',
            'description': 'A single burner stove for cooking food and boiling water',
            'weight': '5 oz'
            },
            {
            'name': 'Tarp',
            'description': 'A single walled shelter made of silnylon',
            'weight': '20 oz'
            },
        ]

class UserGearListHandler(web.RequestHandler):

    @web.asynchronous
    def get(self, user):
        mq = self.application.mq
        correlation_id = str(uuid.uuid4())
        jsonrpc = {
                'jsonrpc': '2.0',
                'method': 'list',
                'params': [user],
                'id': correlation_id
                }
        msg_properties = pika.BasicProperties(
                content_type = 'application/json-rpc',
                correlation_id = correlation_id,
                reply_to = self.application.mq.rpc_reply
                )
        mq.register_rpc_reply(correlation_id, self.respond_to_get)
        mq.channel.basic_publish(
                exchange = 'gear',
                routing_key = 'gear.user.rpc',
                properties = msg_properties,
                body = json.dumps(jsonrpc)
                )

    def respond_to_get(self, headers, body):
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(body)
        self.finish()








