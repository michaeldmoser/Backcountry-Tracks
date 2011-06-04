import unittest
import json

import pika.adapters
import pika.connection
import pika

from tptesting import environment
from tptesting import utils

class TestAdventurerServiceRegistration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()

        cls.environ.start_rabbitmq()
        cls.environ.riak.start()

        mq_params = pika.ConnectionParameters(host='localhost')
        mq_conn = pika.BlockingConnection(mq_params)
        channel = mq_conn.channel()
        channel.exchange_declare(exchange='registration', type='topic')
        cls.channel = channel

        cls.environ.adventurer.start()

        cls.albert = cls.environ.albert

    @classmethod
    def tearDownClass(self):
        self.environ.teardown()

    def test_retrieves_and_saves_regitrations(self):
        """Service should retrieve registrations from rabbitmq and save to riak"""
        registration_message = json.dumps(self.environ.albert)
        properties = pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2
                )

        self.channel.basic_publish(
                exchange='registration',
                routing_key='registration.register',
                properties=properties,
                body=registration_message
                )

        def check_registration_stored():
            try:
                user_bucket = self.environ.riak.get_database('adventurers')
                albert_user = user_bucket.get(self.albert.email)
                albert_data = albert_user.get_data()
            except Exception, e:
                raise AssertionError(str(e))

            self.assertEquals(albert_data, self.albert)
        utils.try_until(1, check_registration_stored)

if __name__ == '__main__':
    unittest.main()

