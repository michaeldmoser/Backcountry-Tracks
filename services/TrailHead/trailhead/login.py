import pika
import uuid
from tornado.web import RequestHandler

class LoginHandler(RequestHandler):
    def post(self):
        mq = self.application.mq
        properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = str(uuid.uuid4()),
                reply_to = self.application.mq.rpc_reply,
                )
        mq.channel.basic_publish(
                exchange = 'adventurer',
                routing_key = 'adventurer.login',
                body = self.request.body,
                properties = properties
                )
        self.set_header('Location', '/app/home')
        self.set_status(303)
