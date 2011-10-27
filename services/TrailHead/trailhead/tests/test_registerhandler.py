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

    def test_returned_status_code_200(self):
        """On a good post should return a 200 Accepted status code"""
        request = faketornado.HTTPRequestFake(
                'post',
                '/app/register',
                headers = {'Content-Type': 'application/json; charset=UTF-8'}
                )
        pika_connection_class = fakepika.SelectConnectionFake()
        application = faketornado.WebApplicationFake()
        application.mq = PikaClient(pika_connection_class, dict())
        application.mq.connect()
        pika_connection_class.ioloop.start()

        handler = RegisterHandler(application(), request)
        handler.post()

        self.assertEquals(handler._status_code, 200)

    def test_returned_status_code_400(self):
        """On a bad post should return a 400 bad data status code"""
        request = faketornado.HTTPRequestFake(
                'post',
                '/app/register',
                headers = {'Content-Type': 'mulitpart/form-data'}
                )
        pika_connection_class = fakepika.SelectConnectionFake()
        application = faketornado.WebApplicationFake()
        application()
        application.mq = PikaClient(pika_connection_class, dict())
        application.mq.connect()
        pika_connection_class.ioloop.start()

        handler = RegisterHandler(application(), request)
        handler.post()

        self.assertEquals(handler._status_code, 400)

class TestPublishesRegistration(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()
        request = faketornado.HTTPRequestFake(
                'post',
                '/app/register',
                headers = {'Content-Type': 'application/json'}
                )
        request.body = json.dumps(self.environ.douglas)

        pika_connection_class = fakepika.SelectConnectionFake()
        application = faketornado.WebApplicationFake()
        application()
        application.mq = PikaClient(pika_connection_class, dict())
        application.mq.connect()
        pika_connection_class.ioloop.start()
        self.application = application
        self.pika = pika_connection_class

        handler = RegisterHandler(application(), request)
        handler.post()

    def test_publish_registration_data(self):
        '''Pushlishes registration data to mq'''
        received_body = json.loads(self.pika.published_messages[0].body)
        self.assertEquals(received_body, self.environ.douglas)

    def test_correct_exchange(self):
        '''Publishes to the correct exchange'''
        actual_exchange = self.pika.published_messages[0].exchange
        self.assertEquals(actual_exchange, 'registration')

    def test_correct_routing_key(self):
        '''Publishes with the correct routing key'''
        actual_routing_key = self.pika.published_messages[0].routing_key
        self.assertEquals(actual_routing_key, 'registration.register')

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

