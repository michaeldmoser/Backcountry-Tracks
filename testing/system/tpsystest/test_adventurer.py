import unittest
import json
from os import path

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
        channel.queue_declare(
                queue = 'registrations',
                durable = False,
                exclusive = False,
                auto_delete = True
                )
        channel.queue_bind(
                exchange = 'registration',
                queue = 'registrations',
                routing_key = 'registration.register'
                )
        cls.channel = channel

        cls.environ.adventurer.start()

        cls.albert = cls.environ.albert

        adventurer_config = cls.environ.get_config_for('adventurer')
        cls.pidfile_path = adventurer_config['pidfile']

    @classmethod
    def tearDownClass(self):
        self.environ.teardown()

    def test_daemonized_process(self):
        '''We should have a running process with a pidfile'''
        def check_for_pidfile():
            assert path.exists(self.pidfile_path), 'PID file does not exist'
        utils.try_until(1, check_for_pidfile)

        pid = open(self.pidfile_path, 'r').read().strip()
        cmdline_path = path.join('/proc', pid, 'cmdline')
        assert path.exists(cmdline_path), 'Could not find the process'

        cmdline = open(cmdline_path, 'r').read()
        assert '/usr/local/bin/adventurer' in cmdline, 'Not the correct process'

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

