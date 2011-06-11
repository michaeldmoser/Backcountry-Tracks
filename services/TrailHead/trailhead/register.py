import json

import pika
from tornado.web import RequestHandler

class RegisterHandler(RequestHandler):
    def post(self):
        if not self.request.headers.get('Content-Type') == 'application/json':
            self.set_status(400)
            return

        mq = self.application.mq
        properties = pika.BasicProperties(
                content_type = 'application/json',
                delivery_mode = 2
                )
        mq.channel.basic_publish(
                exchange = 'registration', 
                routing_key = 'registration.register',
                body = self.request.body,
                properties = properties
                )
        self.set_status(202)

