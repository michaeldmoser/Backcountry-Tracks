import json
import pika
import uuid
from tornado import web
from tornado.web import RequestHandler
from trailhead.login import BaseHandler

class RegisterHandler(BaseHandler):

    def get(self):
        self.set_status(400)
        return

    def post(self):
        if 'application/json' not in self.request.headers.get('Content-Type'):
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

class ActivateHandler(BaseHandler):
    @web.asynchronous
    def get(self, email, confirmation_code):

        data = json.dumps({
            'email': email,
            'confirmation_code': confirmation_code
            })

        mq = self.application.mq
        correlation_id = str(uuid.uuid4())
        properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = correlation_id,
                reply_to = self.application.mq.rpc_reply,
                )
        mq.register_rpc_reply(correlation_id, self.respond_to_request)
        mq.channel.basic_publish(
                exchange = 'registration',
                routing_key = 'registration.activate',
                body = data,
                properties = properties
                )

    def respond_to_request(self, headers, body):
        reply = json.loads(body)
        if reply['successful'] == True:
            self.set_status(303)
            self.set_header('Location', '/app/registration-complete')
        else:
            self.set_status(403)
            self.set_header('Location', '/')
        self.finish()
