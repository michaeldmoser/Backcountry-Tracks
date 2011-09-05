from tornado import web
import pika

import uuid
import json

import logging

from trailhead.login import BaseHandler

class TripsBaseHandler(BaseHandler):

    def json_rpc_request(self, method, params):
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
                reply_to = self.application.mq.rpc_reply,
                delivery_mode = 2
                )
        mq.register_rpc_reply(correlation_id, self.respond_to_request)
        logging.debug('Publish request for trip:\n%s' % jsonrpc)
        mq.channel.basic_publish(
                exchange = 'trips',
                routing_key = 'trips.rpc',
                properties = msg_properties,
                body = json.dumps(jsonrpc),
                )

    def respond_to_request(self, headers, body):
        logging.debug('Received response:\n%s' % body)
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(body)
        self.finish()

class TripsHandler(TripsBaseHandler):
    '''
    Manage a collection of trips: Add to, list, etc
    '''

    @web.authenticated
    @web.asynchronous
    def post(self):
        trip_data = json.loads(self.request.body)
        self.json_rpc_request('create', [self.current_user, trip_data])


class TripHandler(TripsBaseHandler):
    '''
    Manages an individual trip: Update, delete
    '''

    @web.authenticated
    @web.asynchronous
    def put(self, trip_id):
        trip_data = json.loads(self.request.body)
        self.json_rpc_request('update', [self.current_user, trip_id, trip_data])

    @web.authenticated
    def delete(self, trip_id):
        logging.info("Received trip delete for %s:%s" % (self.current_user, trip_id))
        self.json_rpc_request('delete', [self.current_user, trip_id])
        self.set_status(204)

