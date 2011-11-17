import unittest

import json

from tptesting import faketornado, fakepika, environment

from tornado.web import RequestHandler
from trailhead.mq import PikaClient
from trailhead.tests.utils import setup_handler

from adventurer2.register import RegisterHandler, ActivateHandler

class TestRegisterHandler(unittest.TestCase):

    def test_implements_post_method(self):
        """RegisterHandler should be able to respond to HTTP POSTs, in other words it must implement the post() method"""
        self.assertNotEquals(RegisterHandler.post, RequestHandler.post)

    def test_inherits_from_requesthandler(self):
        """Tornado requires inheriting from RequestHandler"""
        assert(issubclass(RegisterHandler, RequestHandler))

class TestRegisterHandlerHttp(unittest.TestCase):

    def test_returned_status_code_200(self):
        """On a good post should return a 200 Accepted status code"""
        environ = environment.create()
        body = json.dumps(environ.albert)
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        handler, application, pika = setup_handler(RegisterHandler, 'POST',
                '/app/register', headers = headers, body=body)

        handler.post()

        self.assertEquals(handler._status_code, 200)

    def test_returned_status_code_400(self):
        """On a bad post should return a 400 bad data status code"""
        headers = {'Content-Type': 'mulitpart/form-data'}
        handler, application, pika = setup_handler(RegisterHandler, 'POST',
                '/app/register', headers = headers)
        handler.post()

        self.assertEquals(handler._status_code, 400)

class TestPublishesRegistration(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()
        body = json.dumps(self.environ.douglas)
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        self.handler, self.application, self.pika = setup_handler(RegisterHandler, 'POST',
                '/app/register', headers = headers, body=body)

        self.handler.post()

    def test_publish_registration_data(self):
        '''Pushlishes registration data to mq'''
        received_body = json.loads(self.pika.published_messages[0].body)
        expected_body = {
                'jsonrpc': '2.0',
                'method': 'register',
                'params': self.environ.douglas,
                'id': self.pika.published_messages[0].properties.correlation_id 
                }
        self.assertEquals(received_body, expected_body)

    def test_correct_exchange(self):
        '''Publishes to the correct exchange'''
        actual_exchange = self.pika.published_messages[0].exchange
        self.assertEquals(actual_exchange, 'adventurer')

    def test_correct_routing_key(self):
        '''Publishes with the correct routing key'''
        actual_routing_key = self.pika.published_messages[0].routing_key
        self.assertEquals(actual_routing_key, 'adventurer.rpc')

    def test_correct_content_type(self):
        '''Publishes message using json mime type'''
        actual_mime_type = self.pika.published_messages[0].properties.content_type
        self.assertEquals(actual_mime_type, 'application/json')

    def test_durablability(self):
        '''Message should be published as durable'''
        actual_durability = self.pika.published_messages[0].properties.delivery_mode
        self.assertEquals(actual_durability, 2)

class TestActivateHandler(unittest.TestCase):
    def setUp(self):
        self.environ = environment.create()
        body = json.dumps(self.environ.douglas)
        self.activate_code = '1234'
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        url = '/app/activate/%s/%s' % (self.environ.douglas.email, self.activate_code)
        self.handler, self.application, self.pika = setup_handler(ActivateHandler, 'POST',
                url, headers=headers, body=body)

        self.handler.get(self.environ.douglas.email, self.activate_code)

    def test_publishes_activation_message(self):
        '''Publishes command message to activate user'''
        command_message_body = json.loads(self.pika.published_messages[0].body)
        expected_body = {
                'jsonrpc': '2.0',
                'method': 'activate',
                'params': [self.environ.douglas.email, self.activate_code],
                'id': self.pika.published_messages[0].properties.correlation_id
                }

        self.assertEquals(command_message_body, expected_body)

    def test_publishes_to_correct_exchange(self):
        '''Publishes command message to the adventurer exchange'''
        published_exchange = self.pika.published_messages[0].exchange
        self.assertEquals(published_exchange, 'adventurer')

    def test_publishes_with_routing_key(self):
        '''Publishes command message with correct routing key'''
        routing_key = self.pika.published_messages[0].routing_key
        self.assertEquals(routing_key, 'adventurer.rpc')

    def test_correct_content_type(self):
        '''Publishes message using json mime type'''
        actual_mime_type = self.pika.published_messages[0].properties.content_type
        self.assertEquals(actual_mime_type, 'application/json')

    def test_durablability(self):
        '''Message should be published as durable'''
        actual_durability = self.pika.published_messages[0].properties.delivery_mode
        self.assertEquals(actual_durability, 2)



if __name__ == '__main__':
    unittest.main()

