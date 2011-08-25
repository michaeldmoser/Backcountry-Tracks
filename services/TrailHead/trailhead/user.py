import logging

import json
import uuid
import pika

from .login import BaseHandler

from tornado import web

class UserHandler(BaseHandler):

    @web.authenticated
    @web.asynchronous
    def get(self):
        logging.info('TrailHead(UserHandler): GET /user (%s)' % self.current_user)
        mq = self.application.mq
        correlation_id = str(uuid.uuid4())
        jsonrpc = {
                'jsonrpc': '2.0',
                'method': 'get',
                'params': [self.current_user],
                'id': correlation_id
                }
        msg_properties = pika.BasicProperties(
                content_type = 'application/json-rpc',
                correlation_id = correlation_id,
                reply_to = self.application.mq.rpc_reply
                )
        mq.register_rpc_reply(correlation_id, self.respond_to_get)
        logging.debug('TrailHead(UserHandler): Publish request to adventurer.rpc (id: %s)' % correlation_id)
        mq.channel.basic_publish(
                exchange = 'adventurer',
                routing_key = 'adventurer.rpc',
                properties = msg_properties,
                body = json.dumps(jsonrpc)
                )

    def respond_to_get(self, headers, body):
        logging.debug('TrailHead(UserHandler): Received response %s' % body)
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(body)
        self.finish()

