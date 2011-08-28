from tornado import web
import pika

import uuid
import json

import logging

from trailhead.login import BaseHandler

class UserGearListHandler(BaseHandler):

    def __json_rpc_request(self, method, params):
        mq = self.application.mq
        correlation_id = str(uuid.uuid4())

        jsonrpc = {
                'jsonrpc': '2.0',
                'method': method,
                'params': params,
                'id': correlation_id
                }
        msg_properties = pika.BasicProperties(
                content_type = 'application/json-rpc',
                correlation_id = correlation_id,
                reply_to = self.application.mq.rpc_reply
                )
        mq.register_rpc_reply(correlation_id, self.respond_to_get)
        logging.debug('Publish request for gear:\n%s' % jsonrpc)
        mq.channel.basic_publish(
                exchange = 'gear',
                routing_key = 'gear.user.rpc',
                properties = msg_properties,
                body = json.dumps(jsonrpc)
                )

    @web.authenticated
    @web.asynchronous
    def get(self, user):
        logging.info('Received request for %s\'s gear list' % user)
        self.__json_rpc_request('list', [user])

    @web.authenticated
    @web.asynchronous
    def post(self, user):
        pieceofgear = json.loads(self.request.body)
        self.__json_rpc_request('create', [user, pieceofgear])

    def respond_to_get(self, headers, body):
        logging.debug('Received response:\n%s' % body)
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(body)
        self.finish()


