from tornado import web
import pika

import uuid
import json

import logging

from trailhead.handlers import BaseHandler

class TripsBaseHandler(BaseHandler):

    def __init__(self, *args, **kwargs):
        BaseHandler.__init__(self, *args, **kwargs)
        self.service = self.application.mq.remoting.service('Trips')
        self.remoting = self.application.mq.remoting

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

    def respond_to_request(self, body):
        logging.debug('Received response:\n%s' % body)
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(body))
        self.finish()

class TripsHandler(TripsBaseHandler):
    '''
    Manage a collection of trips: Add to, list, etc
    '''

    @web.authenticated
    @web.asynchronous
    def post(self):
        trip_data = json.loads(self.request.body)
        command = self.service.create(self.current_user, trip_data)
        command.persistant = True
        self.remoting.call(command, self.respond_to_request)

    @web.authenticated
    @web.asynchronous
    def get(self):
        command = self.service.list(self.current_user)
        self.remoting.call(command, self.respond_to_request)


class TripHandler(TripsBaseHandler):
    '''
    Manages an individual trip: Update, delete
    '''

    @web.authenticated
    @web.asynchronous
    def put(self, trip_id):
        trip_data = json.loads(self.request.body)
        command = self.service.update(self.current_user, trip_id, trip_data)
        command.persistant = True
        self.remoting.call(command, self.respond_to_request)

    @web.authenticated
    def delete(self, trip_id):
        logging.info("Received trip delete for %s:%s" % (self.current_user, trip_id))
        command = self.service.delete(self.current_user, trip_id)
        command.persistant = True
        self.remoting.call(command)
        self.set_status(204)



