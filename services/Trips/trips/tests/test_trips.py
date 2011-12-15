import unittest

import json
import pika
import uuid

from tptesting import faketornado, environment, fakepika, thandlers

from trailhead.tests.utils import create_fake_application, setup_handler

from trips.handlers import TripsHandler, TripHandler

class TestTripCreate(thandlers.TornadoHandlerTestCase):

    def request_handler(self):
        return TripsHandler

    def url(self):
        return '/app/trips'

    def active_user(self):
        return self.environ.ramona.email

    def method(self):
        return 'POST'

    def method_args(self):
        return list(), dict()

    def rpc_result(self):
        trip_data = self.environ.data['trips'][0].copy()
        trip_data.update({'id': '1234'})
        return trip_data

    def http_response(self):
        return self.rpc_result()

    def expected_rpc_request(self):
        return 'create', [self.environ.ramona.email, self.environ.data['trips'][0]]

    def expected_durability(self):
        return True

    def remote_service_name(self):
        return 'Trips'

    def http_request_body(self):
        return json.dumps(self.environ.data['trips'][0])

class TestTripUpdate(thandlers.TornadoHandlerTestCase):
    def setUp(self):
        environ = environment.create()
        self.adventurer = environ.douglas

        self.trip_id = str(uuid.uuid4())
        self.trip = environ.data['trips'][0].copy()
        self.trip['owner'] = self.adventurer.email
        thandlers.TornadoHandlerTestCase.setUp(self)

    def request_handler(self):
        return TripHandler

    def url(self):
        return '/app/trips/%s' % self.trip_id

    def active_user(self):
        return self.adventurer.email

    def method(self):
        return 'PUT'

    def method_args(self):
        return [self.trip_id], dict()

    def rpc_result(self):
        return self.trip

    def http_response(self):
        return self.rpc_result()

    def expected_rpc_request(self):
        return 'update', [self.adventurer.email, self.trip_id, self.trip]

    def expected_durability(self):
        return True

    def remote_service_name(self):
        return 'Trips'

    def http_request_body(self):
        return json.dumps(self.trip)



class TestTripsDelete(unittest.TestCase):
    '''
    Tests the process of receiving a DELETE on /trips/<id>
    and sending a delete json rpc request
    '''

    def setUp(self):
        self.environ = environment.create()
        self.adventurer = self.environ.douglas

        self.trip_id = str(uuid.uuid4())
        url = '/trips/%s' % self.trip_id
        self.handler, self.application, self.pika = setup_handler(TripHandler,
                'DELETE', url, user=self.adventurer.email)
        self.request = self.handler.request

        self.handler.delete(self.trip_id)

        self.sent_message = self.pika.published_messages[0]

    def test_rpc_response(self):
        '''Should return a list of trips for the user'''
        self.handler.finish() # Tornado does this automatically for non-async methods
        headers, body = self.request._output.split('\r\n\r\n')
        self.assertEquals('', body)

    def test_response_status(self):
        '''Should respond with a 204 HTTP status'''
        self.assertEquals(self.handler._status_code, 204)

    def test_send_create_request_body(self):
        '''Sends a JSON-RPC message request for creating a piece of trips'''
        sent_request = json.loads(self.sent_message.body)
        del sent_request['id'] # we don't care about the id in this context

        expected_request = {
                'jsonrpc': '2.0',
                'method': 'delete',
                'params': [self.adventurer.email, self.trip_id],
                }
        self.assertEquals(expected_request, sent_request)

    def test_delivery_mode(self):
        '''Does need to be a persisted message'''
        delivery_mode = self.sent_message.properties.delivery_mode
        self.assertEquals(delivery_mode, 2)

class TestTripsList(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()

        url = '/app/trips'
        self.handler, self.application, self.pika = setup_handler(TripsHandler,
                'GET', url, user=self.environ.douglas.email)
        self.request = self.handler.request

        self.handler.get()
        self.sent_message = self.pika.published_messages[0]

        self.headers = pika.BasicProperties(
                correlation_id = self.sent_message.properties.correlation_id,
                content_type = 'application/json'
                )

        self.rpc_response = {
                'jsonrpc': '2.0',
                'result': self.environ.data['trips'],
                'id': self.sent_message.properties.correlation_id
                }

        reply_queue = self.application.mq.remoting.queue

        self.pika.inject(reply_queue, self.headers, json.dumps(self.rpc_response))
        self.pika.trigger_consume(reply_queue)

    def test_send_request_for_gear_body(self):
        '''Sends a JSON-RPC message request for listing gear'''
        sent_request = json.loads(self.sent_message.body)
        del sent_request['id'] # we don't care about the id in this context

        expected_request = {
                'jsonrpc': '2.0',
                'method': 'list',
                'params': [self.environ.douglas.email],
                }
        self.assertEquals(expected_request, sent_request)

    def test_delivery_mode(self):
        '''Does not need to be a persisted message'''
        delivery_mode = self.sent_message.properties.delivery_mode
        self.assertIsNone(delivery_mode)

    def test_rpc_response(self):
        '''Should return a list of trips for the user'''
        headers, body = self.request._output.split('\r\n\r\n')
        response = json.loads(body)
        self.assertEquals(self.rpc_response['result'], response)

if __name__ == "__main__":
    unittest.main()

