import unittest

import json
from tptesting import faketornado, environment, fakepika

from trailhead.mq import PikaClient
from trailhead.login import LoginHandler

class TestValidLogin(unittest.TestCase):
    def setUp(self):
        environ = environment.create()

        request = faketornado.HTTPRequestFake(
                'post', 
                '/app/login',
                headers = {'Content-Type': 'application/json'}
                )
        request.body = json.dumps({
            'email': environ.ramona.email,
            'password': environ.ramona.password,
            })

        pika_connection_class = fakepika.SelectConnectionFake()
        application = faketornado.WebApplicationFake()
        application()
        application.mq = PikaClient(pika_connection_class, dict())
        application.mq.connect()
        application.mq.rpc_reply = ''
        pika_connection_class.ioloop.start()

        self.handler = LoginHandler(application, request)

    def test_status_code(self):
        """Should use a 303 status code"""
        self.handler.post()
        self.assertEquals(self.handler._status_code, 303)

    def test_redirects_to_home(self):
        """Should set location header"""
        self.handler.post()
        location = self.handler._headers['Location']
        self.assertEquals(location, '/app/home')

class TestSendsLoginRequest(unittest.TestCase):
    def setUp(self):
        environ = environment.create()

        self.credentials = {
            'email': environ.ramona.email,
            'password': environ.ramona.password,
            }
        request = faketornado.HTTPRequestFake(
                'post', 
                '/app/login',
                headers = {'Content-Type': 'application/json'}
                )
        request.body = json.dumps(self.credentials)

        pika_connection_class = fakepika.SelectConnectionFake()
        self.application = faketornado.WebApplicationFake()
        self.application()
        self.application.mq = PikaClient(pika_connection_class, dict())
        self.application.mq.connect()
        pika_connection_class.ioloop.start()
        self.pika = pika_connection_class

        self.handler = LoginHandler(self.application, request)
        self.handler.post()

    def test_sends_login_request_message(self):
        '''Sends the login request through RabbitMQ'''
        message = self.pika.published_messages[0]
        sent_credentials = json.loads(message.body)

        self.assertEquals(sent_credentials, self.credentials)

    def test_exchange_used(self):
        '''Uses the adventurer exchange'''
        message = self.pika.published_messages[0]
        self.assertEquals(message.exchange, 'adventurer')

    def test_routing_key(self):
        '''Uses the correct routing key'''
        message = self.pika.published_messages[0]
        self.assertEquals(message.routing_key, 'adventurer.login')

    def test_content_type(self):
        '''Uses json content type'''
        message = self.pika.published_messages[0]
        self.assertEquals(message.properties.content_type, 'application/json')

    def test_delivery_mode(self):
        '''Does not need to be a persistented message'''
        message = self.pika.published_messages[0]
        self.assertEquals(message.properties.delivery_mode, None)

    def test_correlation_id(self):
        '''Test that a correlation_id is set'''
        properties = self.pika.published_messages[0].properties
        self.assertIsNotNone(properties.correlation_id)

    def test_reply_to(self):
        '''Test that the reply_to is set correctly'''
        properties = self.pika.published_messages[0].properties
        self.assertEquals(properties.reply_to, self.application.mq.rpc_reply)

        
if __name__ == '__main__':
    unittest.main()

