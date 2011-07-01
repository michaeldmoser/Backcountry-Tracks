import unittest

import urllib2
import json
import threading
import time

import pika
from pika import spec

from tptesting import environment, utils

class TestLoginHTTPPost(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()

        mq_params = pika.ConnectionParameters(host='localhost')
        mq_conn = pika.BlockingConnection(mq_params)
        cls.channel = mq_conn.channel()

        login_url = cls.environ.trailhead_url + '/login'
        cls.credentials = {
                'email': cls.environ.douglas.email,
                'password': cls.environ.douglas.password
                }
        cls.login_request = urllib2.Request(
                login_url,
                json.dumps(cls.credentials),
                headers = {'Content-Type': 'application/json'}
                )
        def make_request():
            cls.response = urllib2.urlopen(cls.login_request)
        request_thread = threading.Thread(target=make_request)
        request_thread.start()

        def wait_for_message():
            for x in range(20):
                method, headers, body = cls.channel.basic_get(queue='login_rpc')
                if isinstance(method, spec.Basic.GetOk):
                    return method, headers, body

                time.sleep(0.1)

            assert False, "Failed to get a message in the alotted time"

        cls.method, cls.headers, cls.body = wait_for_message()

    @classmethod
    def tearDownClass(cls):
        cls.environ.teardown()


    def test_login_redirects(self):
        """Valid credentials should redirect to application home"""
        expected_url = self.environ.trailhead_url + "/home"
        self.assertEquals(self.response.url, expected_url)

    def test_login_message(self):
        '''A login message should be sent to the Adventurer service'''
        received_credentials = json.loads(self.body)
        self.assertEquals(self.credentials, received_credentials)

    def test_login_message_headers_correlation_id(self):
        '''Login message should have a correlation_id'''
        self.assertIsNotNone(self.headers.correlation_id)

    def test_login_message_headers_reply_to(self):
        '''Login message should have a reply_to'''
        self.assertIsNotNone(self.headers.reply_to)
        
class TestLoginHTTPResponse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.response = None
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()

        mq_params = pika.ConnectionParameters(host='localhost')
        mq_conn = pika.BlockingConnection(mq_params)
        cls.channel = mq_conn.channel()

        login_url = cls.environ.trailhead_url + '/login'
        cls.credentials = {
                'email': cls.environ.douglas.email,
                'password': cls.environ.douglas.password
                }
        cls.login_request = urllib2.Request(
                login_url,
                json.dumps(cls.credentials),
                headers = {'Content-Type': 'application/json'}
                )
        def make_request():
            cls.response = urllib2.urlopen(cls.login_request)
        request_thread = threading.Thread(target=make_request)
        request_thread.start()

        def wait_for_message():
            for x in range(20):
                method, headers, body = cls.channel.basic_get(queue='login_rpc')
                if isinstance(method, spec.Basic.GetOk):
                    return method, headers, body

                time.sleep(0.1)

            assert False, "Failed to get a message in the alotted time"

        cls.method, cls.headers, cls.body = wait_for_message()
        
    def test_send_invalid_login_response(self):
        '''Receiving and invalid login response produces an invalid login page'''
        invalid_login_reply = {
                'successful': False
                }

        properties = pika.BasicProperties(
                correlation_id = self.headers.correlation_id,
                content_type = 'application/json'
                )
        self.channel.basic_publish(
                exchange = 'adventurer',
                routing_key = 'adventurer.login.%s' % self.headers.reply_to,
                properties = properties,
                body = json.dumps(invalid_login_reply)
                )

        def wait_for_response():
            assert self.response is not None
        utils.try_until(1, wait_for_response)

        self.assertIn('/app/login', self.response.url)

    def test_send_valid_login_response(self):
        '''Receiving a valid login response produces the home page'''
        invalid_login_reply = {
                'successful': True
                }

        properties = pika.BasicProperties(
                correlation_id = self.headers.correlation_id,
                content_type = 'application/json'
                )
        self.channel.basic_publish(
                exchange = 'adventurer',
                routing_key = 'adventurer.login.%s' % self.headers.reply_to,
                properties = properties,
                body = json.dumps(invalid_login_reply)
                )

        def wait_for_response():
            assert self.response is not None
        utils.try_until(1, wait_for_response)

        self.assertIn('/app/home', self.response.url)



if __name__ == '__main__':
    unittest.main()

