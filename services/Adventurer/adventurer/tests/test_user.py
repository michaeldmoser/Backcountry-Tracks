import unittest

import json, pika
from tptesting import faketornado, environment, fakepika
from trailhead.tests.utils import setup_handler
from tornado.web import HTTPError

from adventurer.user import UserHandler

class TestUserHandlerGet(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()

        url = '/app/user'
        handler, self.application, pika = setup_handler(UserHandler, 'GET', 
                url, self.environ.douglas.email)

        handler.get()

        self.sent_message = pika.published_messages[0]


    def test_sends_request_for_user_info(self):
        sent_request = json.loads(self.sent_message.body)
        del sent_request['id'] # we don't care about the id in this context

        expected_request = {
                'jsonrpc': '2.0',
                'method': 'get',
                'params': [self.environ.douglas.email],
                }
        self.assertEquals(expected_request, sent_request)

    def test_delivery_mode(self):
        '''Does not need to be a persisted message'''
        delivery_mode = self.sent_message.properties.delivery_mode
        self.assertIsNone(delivery_mode)

    def test_correlation_id_jsonrpc_id(self):
        '''The messages correlation_id and the json-rpc id should be the same'''
        sent_request = json.loads(self.sent_message.body)
        json_id = sent_request['id']
        correlation_id = self.sent_message.properties.correlation_id

        self.assertEquals(json_id, correlation_id)

class TestUserHandlerReply(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()

        url = '/app/user'
        self.handler, self.application, pika_connection = setup_handler(UserHandler,
                'GET',  url, self.environ.douglas.email)

        self.handler.get()

        self.sent_message = pika_connection.published_messages[0]

        self.headers = pika.BasicProperties(
                correlation_id = self.sent_message.properties.correlation_id,
                content_type = 'application/json'
                )


        self.response = {
                'jsonrpc': '2.0',
                'result': self.environ.douglas,
                'id': self.sent_message.properties.correlation_id,
                }

        reply_queue = self.application.mq.remoting.queue
        pika_connection.inject(reply_queue, self.headers,
                json.dumps(self.response))
        pika_connection.trigger_consume(reply_queue)

    def test_gear_list_response(self):
        '''Should return a list of gear for the user'''
        headers, body = self.handler.request._output.split('\r\n\r\n')
        actual_user = json.loads(body)
        self.assertEquals(self.environ.douglas, actual_user)

    def test_response_status(self):
        '''Should respond with a 200 HTTP status'''
        self.assertEquals(self.handler._status_code, 200)

    def test_finishes_request(self):
        '''Reports being finished to tornado'''
        self.assertTrue(self.handler.request.was_called(self.handler.request.finish))

class TestNotLoggedIn(unittest.TestCase):

    def test_not_logged_in(self):
        '''Should raise an HTTPError 403'''
        self.environ = environment.create()

        url = '/app/user'
        handler, self.application, pika = setup_handler(UserHandler, 'GET', 
                url)

        handler.get()

        self.assertEquals(handler.get_status(), 403)



if __name__ == '__main__':
    unittest.main()

