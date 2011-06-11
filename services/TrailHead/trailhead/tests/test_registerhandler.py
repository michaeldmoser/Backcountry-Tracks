import unittest

import json

from tptesting import faketornado, fakepika, environment

from tornado.web import RequestHandler
from trailhead.register import RegisterHandler
from trailhead.mq import PikaClient

class TestRegisterHandler(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_implements_post_method(self):
        """RegisterHandler should be able to respond to HTTP POSTs, in other words it must implement the post() method"""
        self.assertNotEquals(RegisterHandler.post, RequestHandler.post)

    def test_inherits_from_requesthandler(self):
        """Tornado requires inheriting from RequestHandler"""
        assert(issubclass(RegisterHandler, RequestHandler))

class TestRegisterHandlerHttp(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_returned_status_code(self):
        """On a good post should return a 202 Accepted status code"""
        request = faketornado.HTTPRequestFake(
                'post', 
                '/app/register',
                headers = {'Content-Type': 'application/json'}
                )
        application = faketornado.WebApplicationFake()
        application.mq = PikaClient(fakepika.PikaConnectionFake, dict())
        application.mq.connect()
        handler = RegisterHandler(application, request)
        handler.post()
        
        self.assertEquals(handler._status_code, 202)

    def test_returned_status_code(self):
        """On a good post should return a 202 Accepted status code"""
        request = faketornado.HTTPRequestFake(
                'post', 
                '/app/register',
                headers = {'Content-Type': 'mulitpart/form-data'}
                )
        application = faketornado.WebApplicationFake()
        application.mq = PikaClient(fakepika.PikaConnectionFake, dict())
        application.mq.connect()
        handler = RegisterHandler(application, request)
        handler.post()
        
        self.assertEquals(handler._status_code, 400)

class TestPublishesRegistration(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()
        class PikaConnectionFake(object):
            def __call__(fake, params, on_open_callback=None):
                on_open_callback(fake)

            def channel(fake, callback=None):
                class PikaChannel(object):
                    def basic_publish(self, exchange=None, routing_key=None, body=None, properties=None):
                        fake.message_body = body
                        fake.exchange = exchange
                        fake.routing_key = routing_key
                        fake.properties = properties

                if callback is not None:
                    callback(PikaChannel())

        request = faketornado.HTTPRequestFake(
                'post', 
                '/app/register',
                headers = {'Content-Type': 'application/json'}
                )
        request.body = json.dumps(self.environ.douglas)

        application = faketornado.WebApplicationFake()
        application.mq = PikaClient(PikaConnectionFake(), dict())
        application.mq.connect()
        self.application = application

        handler = RegisterHandler(application, request)
        handler.post()

    def test_publish_registration_data(self):
        '''Pushlishes registration data to mq'''
        received_body = json.loads(self.application.mq.connection.message_body)
        self.assertEquals(received_body, self.environ.douglas)

    def test_correct_exchange(self):
        '''Publishes to the correct exchange'''
        actual_exchange = self.application.mq.connection.exchange
        self.assertEquals(actual_exchange, 'registration')

    def test_correct_routing_key(self):
        '''Publishes with the correct routing key'''
        actual_routing_key = self.application.mq.connection.routing_key
        self.assertEquals(actual_routing_key, 'registration.register')

    def test_correct_content_type(self):
        '''Publishes message using json mime type'''
        actual_mime_type = self.application.mq.connection.properties.content_type
        self.assertEquals(actual_mime_type, 'application/json')

    def test_durablability(self):
        '''Message should be published as durable'''
        actual_durability = self.application.mq.connection.properties.delivery_mode
        self.assertEquals(actual_durability, 2)

if __name__ == '__main__':
    unittest.main()

