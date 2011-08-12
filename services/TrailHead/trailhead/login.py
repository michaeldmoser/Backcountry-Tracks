import pika
import uuid
import json
from tornado import web

class LoginHandler(web.RequestHandler):
    @web.asynchronous
    def post(self):
        if 'application/json' not in self.request.headers.get('Content-Type'):
            self.set_status(400)
            self.finish()
            return

        mq = self.application.mq
        correlation_id = str(uuid.uuid4())
        properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = correlation_id,
                reply_to = self.application.mq.rpc_reply,
                )
        mq.register_rpc_reply(correlation_id, self.respond_to_login)
        mq.channel.basic_publish(
                exchange = 'adventurer',
                routing_key = 'adventurer.login',
                body = self.request.body,
                properties = properties
                )

    def respond_to_login(self, headers, body):
        reply = json.loads(body)
        if reply['successful'] == True:
            self.set_header('X-Location', '/app/home')
            self.set_status(202)
        else:
            self.set_header('X-Location', '/')
            self.set_status(403)

        self.finish()

