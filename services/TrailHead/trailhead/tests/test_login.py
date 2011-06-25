import unittest

import json
import pika
from tptesting import faketornado, environment, fakepika

from trailhead.mq import PikaClient
from trailhead.login import LoginHandler

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

class TestLoginReply(unittest.TestCase):

    def setUp(self):
        environ = environment.create()

        self.credentials = {
            'email': environ.ramona.email,
            'password': environ.ramona.password,
            }
        self.request = faketornado.HTTPRequestFake(
                'post', 
                '/app/login',
                headers = {'Content-Type': 'application/json'}
                )
        self.request.body = json.dumps(self.credentials)

        pika_connection_class = fakepika.SelectConnectionFake()
        self.application = faketornado.WebApplicationFake()
        self.application()
        self.application.mq = PikaClient(pika_connection_class, dict())
        self.application.mq.connect()
        pika_connection_class.ioloop.start()
        self.pika = pika_connection_class

        self.handler = LoginHandler(self.application, self.request)
        self.handler.post()
        self.handler._transforms = []

        login_request = self.pika.published_messages[0]
        self.headers = pika.BasicProperties(
                correlation_id = login_request.properties.correlation_id,
                content_type = 'application/json'
                )

    def test_process_valid_login_reply(self):
        '''Uses 303 status code for valid login'''
        body = json.dumps(dict(successful = True))
        reply_queue = self.application.mq.rpc_reply
        self.pika.inject(reply_queue, self.headers, body)
        self.pika.trigger_consume(reply_queue)

        self.assertEquals(self.handler._status_code, 303)

    def test_process_valid_login_location(self):
        '''Sets location to /app/home'''
        body = json.dumps(dict(successful = True))
        reply_queue = self.application.mq.rpc_reply
        self.pika.inject(reply_queue, self.headers, body)
        self.pika.trigger_consume(reply_queue)

        location = self.handler._headers['Location']
        self.assertEquals(location, '/app/home')

    def test_process_invalid_login_status(self):
        '''Uses 403 forbidden status code on invalid login'''
        body = json.dumps(dict(successful = False))
        reply_queue = self.application.mq.rpc_reply
        self.pika.inject(reply_queue, self.headers, body)
        self.pika.trigger_consume(reply_queue)

        self.assertEquals(self.handler._status_code, 403)

    def test_process_invalid_login_location(self):
        '''Sets location to /app/login'''
        body = json.dumps(dict(successful = False))
        reply_queue = self.application.mq.rpc_reply
        self.pika.inject(reply_queue, self.headers, body)
        self.pika.trigger_consume(reply_queue)

        location = self.handler._headers['Location']
        self.assertEquals(location, '/app/login')

    def test_finishes_request(self):
        '''Report being finished to tornado'''
        body = json.dumps(dict(successful = False))
        reply_queue = self.application.mq.rpc_reply
        self.pika.inject(reply_queue, self.headers, body)
        self.pika.trigger_consume(reply_queue)

        self.assertTrue(self.request.was_called(self.request.finish))
    



        
if __name__ == '__main__':
    unittest.main()

