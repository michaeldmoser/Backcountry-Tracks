import unittest

import json
import pika
from tptesting import faketornado, environment, fakepika, fakeriak
from trailhead.tests.utils import setup_handler

from adventurer2.tests.test_registration import FakeMailer
from adventurer2.login import LoginHandler
from adventurer2.service import AdventurerRepository

class TestLoginHTTPRequest(unittest.TestCase):
    def setUp(self):
        environ = environment.create()

        self.credentials = {
            'email': environ.ramona.email,
            'password': environ.ramona.password,
            }

        body = json.dumps(self.credentials);
        headers = {'Content-Type': 'multipart/form-data'}
        self.handler, self.application, self.pikd = setup_handler(LoginHandler,
                'POST', '/app/login',  body=body, headers=headers)
        self.request = self.handler.request

        self.handler.post()

    def test_rejects_non_json_content(self):
        '''Should not accept non-json content'''
        self.assertEquals(self.handler._status_code, 400)

    def test_finishes_request(self):
        '''Inform tornado the request is finished'''
        self.assertTrue(self.request.was_called(self.request.finish))
        

class TestSendsLoginRequest(unittest.TestCase):

    def setUp(self):
        environ = environment.create()

        self.credentials = {
            'email': environ.ramona.email,
            'password': environ.ramona.password,
            }

        body = json.dumps(self.credentials);
        headers = {'Content-Type': 'application/json'}
        self.handler, self.application, self.pika = setup_handler(LoginHandler,
                'POST', '/app/login',  body=body, headers=headers)
        self.request = self.handler.request

        self.handler.post()

    def test_sends_login_request_message(self):
        '''Sends the login request through RabbitMQ'''
        message = self.pika.published_messages[0]
        sent_message = json.loads(message.body)
        expected_message = {
                'jsonrpc': '2.0',
                'method': 'login',
                'params': self.credentials,
                'id': self.pika.published_messages[0].properties.correlation_id
                }

        self.assertEquals(sent_message, expected_message)

    def test_exchange_used(self):
        '''Uses the adventurer exchange'''
        message = self.pika.published_messages[0]
        self.assertEquals(message.exchange, 'adventurer')

    def test_routing_key(self):
        '''Uses the correct routing key'''
        message = self.pika.published_messages[0]
        self.assertEquals(message.routing_key, 'adventurer.rpc')

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

        body = json.dumps(self.credentials);
        headers = {'Content-Type': 'application/json'}
        self.handler, self.application, self.pika = setup_handler(LoginHandler,
                'POST', '/app/login',  body=body, headers=headers)
        self.request = self.handler.request

        self.handler.post()

        login_request = self.pika.published_messages[0]
        self.headers = pika.BasicProperties(
                correlation_id = login_request.properties.correlation_id,
                content_type = 'application/json'
                )

    def test_process_valid_login_reply(self):
        '''Uses 202 status code for valid login'''
        body = json.dumps(dict(successful = True, email = 'test@example.org'))
        reply_queue = self.application.mq.rpc_reply
        self.pika.inject(reply_queue, self.headers, body)
        self.pika.trigger_consume(reply_queue)

        self.assertEquals(self.handler._status_code, 202)

    def test_process_valid_login_location(self):
        '''Sets location to /app/home when login successful'''
        body = json.dumps(dict(successful = True, email = 'test@example.org'))
        reply_queue = self.application.mq.rpc_reply
        self.pika.inject(reply_queue, self.headers, body)
        self.pika.trigger_consume(reply_queue)

        headers, body = self.request._output.split('\r\n\r\n')
        actual_location = json.loads(body)
        expected_location = {'location': '/app/home'}

        self.assertEquals(actual_location, expected_location)

    def test_process_invalid_login_status(self):
        '''Uses 403 forbidden status code on invalid login'''
        body = json.dumps(dict(successful = False))
        reply_queue = self.application.mq.rpc_reply
        self.pika.inject(reply_queue, self.headers, body)
        self.pika.trigger_consume(reply_queue)

        self.assertEquals(self.handler._status_code, 403)

    def test_process_invalid_login_location(self):
        '''Sets location to /app/login when login invalid'''
        body = json.dumps(dict(successful = False, email = 'test@example.org'))
        reply_queue = self.application.mq.rpc_reply
        self.pika.inject(reply_queue, self.headers, body)
        self.pika.trigger_consume(reply_queue)

        headers, body = self.request._output.split('\r\n\r\n')
        actual_location = json.loads(body)
        expected_location = {'location': '/app/login'}

        self.assertEquals(actual_location, expected_location)

    def test_finishes_request(self):
        '''Report being finished to tornado'''
        body = json.dumps(dict(successful = False))
        reply_queue = self.application.mq.rpc_reply
        self.pika.inject(reply_queue, self.headers, body)
        self.pika.trigger_consume(reply_queue)

        self.assertTrue(self.request.was_called(self.request.finish))


class TestAdventurerRepositoryLogin(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()
        self.riak = fakeriak.RiakClientFake()
        self.bucket_name = 'adventurers'
        self.bucket = self.riak.bucket(self.bucket_name)
        self.fakemail = FakeMailer()

        albert = self.environ.albert
        albert.mark_registered()
        self.bucket.add_document(albert.email, albert)

        self.app = AdventurerRepository(
                bucket_name = self.bucket_name, 
                mailer = self.fakemail, 
                db = self.riak
                )

    def test_login_successful(self):
        '''Returns successful message on valid credentials'''
        login_result = self.app.login(email=self.environ.albert.email,
                password=self.environ.albert.password)
        expected_result = {
                'successful': True,
                'email': self.environ.albert.email
                }
        self.assertEquals(expected_result, login_result)

    def test_login_invalid(self):
        '''Returns false on bad password'''
        login_result = self.app.login(email=self.environ.albert.email, password='badpassword')
        expected_result = {
                'successful': False,
                'email': self.environ.albert.email
                }
        self.assertEquals(expected_result, login_result)

    def test_login_casts_unicode_email_to_string(self):
        """Login allows Unicode email"""
        username = unicode(self.environ.albert.email)
        password = self.environ.albert.password
        login_result = self.app.login(email=username, password=password)

        expected_result = {
                'successful': True,
                'email': self.environ.albert.email
                }
        self.assertEquals(expected_result, login_result)

    def test_not_registered(self):
        '''User has not completed registration'''
        ramona = self.environ.ramona
        self.bucket.add_document(ramona.email, ramona)

        login_result = self.app.login(email=ramona.email, password=ramona.password)
        expected_result = {
                'successful': False,
                'email': ramona.email
                }
        self.assertEquals(expected_result, login_result)

    def test_user_not_found(self):
        '''User does not exist'''
        login_result = self.app.login('nouser', 'nopassword')
        expected_result = {
                'successful': False,
                'email': 'nouser'
                }
        self.assertEquals(expected_result, login_result)

         


if __name__ == '__main__':
    unittest.main()

