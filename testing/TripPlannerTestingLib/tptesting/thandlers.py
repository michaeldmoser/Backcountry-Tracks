import unittest

import json
import pika
import uuid

from tptesting import faketornado, environment, fakepika

from trailhead.tests.utils import create_fake_application, setup_handler



class TornadoHandlerTestCase(unittest.TestCase):

    def request_handler(self):
        raise NotImplementedError("You must define a request_handler() method.")

    def url(self):
        '''Return the url of the request should operate against'''
        raise NotImplementedError("You must define a url() method.")

    def active_user(self):
        '''Return the email address of a user to create an HTTP session with. Return None for no session'''
        raise NotImplementedError("You must define an active_user() method.")

    def method(self):
        '''Return the HTTP method to use for the request'''
        raise NotImplementedError("You must define a method() method")

    def method_args(self):
        '''Return a tuple with two indexes. The first will be used as the position arguments to the request method and the second will be used as the keyword arguments'''
        raise NotImplementedError("You must define a method_args() method")

    def rpc_result(self):
        '''Return the result that would be received via json-rpc over the message over. Should be a list() or a dict()'''
        raise NotImplementedError("You must define a result() method")

    def http_response(self):
        '''What the HTTP response body should be. Return a json encodable entity or None for no response body'''
        raise NotImplementedError('You must define an http_response() method')

    def remote_service_name(self):
        '''The name of the remote service'''
        raise NotImplementedError('You must define a remote_service_name() method')

    def http_request_body(self):
        '''The body of the http request'''
        return None

    def http_status_code(self):
        '''The http status code to expect'''
        return 200

    def handler_setup(self):
        '''Called before all other methods. Allows you to do any setup work required for the tests to run'''
        pass

    def setUp(self):
        self.environ = environment.create()
        self.handler_setup()
        handler = self.request_handler()
        method_name = self.method()
        url = self.url()
        user = self.active_user()
        body = self.http_request_body()
        self.handler, self.application, self.pika = setup_handler(handler, method_name,
                url, user=user, body=body, headers={'Content-Type': 'application/json'})
        self.request = self.handler.request

        args, kwargs = self.method_args()
        method = getattr(self.handler, method_name.lower())
        method(*args, **kwargs)

        self.sent_message = self.pika.published_messages[0]

        self.headers = pika.BasicProperties(
                correlation_id = self.sent_message.properties.correlation_id,
                content_type = 'application/json'
                )

        self.jsonrpc_response = {
                'jsonrpc': '2.0',
                'result': self.rpc_result(),
                'id': self.sent_message.properties.correlation_id,
                }

        reply_queue = self.application.mq.remoting.queue

        self.pika.inject(reply_queue, self.headers, json.dumps(self.jsonrpc_response))
        self.pika.trigger_consume(reply_queue)

    def test_response(self):
        '''Should return a list of gear for the user'''
        headers, body = self.request._output.split('\r\n\r\n')
        actual_result = json.loads(body) if len(body) > 0 else body
        expected_response = self.http_response()
        self.assertEquals(expected_response, actual_result)

    def test_response_status(self):
        '''Should respond with a 200 HTTP status'''
        self.assertEquals(self.handler._status_code, self.http_status_code())

    def test_finishes_request(self):
        '''Reports being finished to tornado'''
        self.assertTrue(self.request.was_called(self.request.finish))

    def test_send_message(self):
        '''Should send a valid JSON RPC message'''
        method, params = self.expected_rpc_request()
        expected_message = {
                'jsonrpc': '2.0',
                'method': method,
                'params': params,
                'id': self.sent_message.properties.correlation_id,
                }
        actual_message = json.loads(self.sent_message.body)
        self.assertEquals(actual_message, expected_message)

    def test_message_durability(self):
        '''Test message durability'''
        expected_durability = 2 if self.expected_durability() else None
        actual_durability = self.sent_message.properties.delivery_mode
        self.assertEquals(actual_durability, expected_durability)

    def test_exchange(self):
        '''Should send to correct exchange'''
        expected_exchange = self.application.mq.remoting.exchange
        actual_exchange = self.sent_message.exchange
        self.assertEquals(actual_exchange, expected_exchange)

    def test_remote_service_name(self):
        '''Remote service name should be'''
        expected_name = "rpc.%s" % self.remote_service_name().lower()
        actual_name = self.sent_message.routing_key
        self.assertEquals(actual_name, expected_name)

