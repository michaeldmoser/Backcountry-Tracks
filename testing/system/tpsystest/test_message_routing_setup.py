import unittest

import subprocess

from tptesting import environment

class TestRegistrationRouting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()

        cls.rabbitmq = cls.environ.rabbitmq
        cls.rabbitmq.start()
        cls.exchanges = cls.rabbitmq.list_exchanges()
        cls.queues = cls.rabbitmq.list_queues()
        cls.bindings = cls.rabbitmq.list_bindings()

    @classmethod
    def tearDownClass(cls):
        cls.environ.teardown()

    def test_registration_exchange(self):
        """The registration exchange is created"""
        self.assertIn('registration', self.exchanges)

    def test_registration_exchange_config(self):
        '''The registration exchange configuration'''
        actual_registration = self.exchanges.get('registration', {})
        expected_registration = {
                'type': 'topic',
                'durable': True,
                'auto_delete': False,
                'internal': False,
                'arguments': '[]'
                }
        self.assertEquals(actual_registration, expected_registration)

    def test_register_queue_exists(self):
        '''The register queue should exist'''
        self.assertIn('register', self.queues)

    def test_register_queue_config(self):
        '''register queue should be durable, no auto_delete, and no args'''
        actual_register = self.queues.get('register', {})
        expected_register = {
                'durable': True,
                'auto_delete': False,
                'arguments': '[]',
                }
        self.assertEquals(actual_register, expected_register)

    def test_binding_exists(self):
        '''A bind between the registration exchange and register queue should exist'''
        binding_needle = {
                'source_name': 'registration',
                'source_kind': 'exchange',
                'destination_name': 'register',
                'destination_kind': 'queue',
                'routing_key': 'registration.register',
                'arguments': '[]',
                }
        self.assertIn(binding_needle, self.bindings)


if __name__ == '__main__':
    unittest.main()
