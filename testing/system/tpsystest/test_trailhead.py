import unittest

import urllib2
import json
import pika

from tptesting import environment, utils

class TestSubmitRegistration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.start_rabbitmq()

        mq_params = pika.ConnectionParameters('localhost')
        mq_conn = pika.BlockingConnection(mq_params)
        channel = mq_conn.channel()
        channel.exchange_declare(
                exchange='registration',
                type='topic',
                auto_delete=True,
                durable=False
                )
        channel.queue_declare(queue='test_registration', durable=False, 
                exclusive=True, auto_delete=True)
        channel.queue_bind(
                exchange='registration',
                queue='test_registration',
                routing_key='registration.register'
                )
        cls.channel = channel

        cls.environ.start_trailhead()

        register_url = '/'.join([cls.environ.trailhead_url, 'register'])
        cls.register_request = urllib2.Request(register_url)

        cls.albert = cls.environ.albert
        cls.register_request.add_data(json.dumps(cls.albert))

    @classmethod
    def tearDownClass(cls):
        cls.environ.teardown()

    def test_submit_valid_registration(self):
        """Submitting a valid registration should return successful"""
        def assert_valid_response():
            try:
                response = urllib2.urlopen(self.register_request)
            except urllib2.HTTPError, e:
                self.fail(str(e))

            status_code = response.code
            self.assertEquals(status_code, 202)

            response_data = response.read()
            self.assertEquals(len(response_data), 0)

        utils.try_until(1, assert_valid_response)

    def test_submit_valid_registration_saved(self):
        '''Submitting a valid registration should create a new user'''

        def submit_registration():
            try:
                response = urllib2.urlopen(self.register_request)
            except urllib2.HTTPError:
                self.fail(str(e))
        utils.try_until(1, submit_registration)

        method, header, body = self.channel.basic_get(queue='test_registration')
        actual_registration = json.loads(body)
        self.assertEquals(actual_registration, self.albert)

                


if __name__ == '__main__':
    unittest.main()
