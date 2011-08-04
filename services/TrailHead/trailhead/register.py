import json

import pika
from tornado.web import RequestHandler

class RegisterHandler(RequestHandler):
    def get(self):
        self.set_status(400)
        return

    def post(self):
        if 'application/json' not in self.request.headers.get('Content-Type'):
            self.set_status(400)
            return

        try:
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
        except Exception as e:
            import syslog
            syslog.syslog(str(e))

