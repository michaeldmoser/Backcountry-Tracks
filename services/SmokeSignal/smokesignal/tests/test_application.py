import unittest

from tptesting import fakepika
from smokesignal.application import SmokeSignalApp

class TestSmokeSignalAppRegistration(unittest.TestCase):
    def setUp(self):
        self.pika_class = fakepika.BlockingConnectionFake()
        pika_connection = self.pika_class()

        app = SmokeSignalApp(pika_connection)
        app.run()

    def test_creates_exchange(self):
        '''Creates the registration exchange'''
        expected_exchange_declare = {
            'type': 'topic',
            'durable': True,
            'auto_delete': False,
            'internal': False,
            'arguments': {}
            }
        actual_exchange = self.pika_class.get_exchange_declaration('registration')
        self.assertDictContainsSubset(expected_exchange_declare, actual_exchange)

    def test_creates_queue(self):
        '''Creates the register queue'''
        expected_queue_declare = {
            'durable': True,
            'auto_delete': False,
            'arguments': {}
            }
        actual_queue = self.pika_class.get_queue_declaration('register')
        self.assertDictContainsSubset(expected_queue_declare, actual_queue)

    def test_creates_binding(self):
        '''Creates the exchange<->queue binding'''
        expected_binding = {
            'queue': 'register',
            'exchange': 'registration',
            'routing_key': 'registration.register',
            }
        actual_binding = self.pika_class.find_binding(expected_binding)
        self.assertDictContainsSubset(expected_binding, actual_binding)

class TestSmokeSignalAppLogin(unittest.TestCase):
    def setUp(self):
        self.pika_class = fakepika.BlockingConnectionFake()
        pika_connection = self.pika_class()

        app = SmokeSignalApp(pika_connection)
        app.run()

    def test_creates_exchange(self):
        '''Creates the adventurer exchange'''
        expected_exchange_declare = {
            'type': 'topic',
            'durable': True,
            'auto_delete': False,
            'internal': False,
            'arguments': {}
            }
        actual_exchange = self.pika_class.get_exchange_declaration('adventurer')
        self.assertDictContainsSubset(expected_exchange_declare, actual_exchange)

    def test_creates_queue(self):
        '''Creates the login queue'''
        expected_queue_declare = {
            'durable': True,
            'auto_delete': False,
            'arguments': {}
            }
        actual_queue = self.pika_class.get_queue_declaration('login_rpc')
        self.assertDictContainsSubset(expected_queue_declare, actual_queue)

    def test_creates_binding(self):
        '''Creates the exchange<->queue binding'''
        expected_binding = {
            'queue': 'login_rpc',
            'exchange': 'adventurer',
            'routing_key': 'adventurer.login',
            }
        actual_binding = self.pika_class.find_binding(expected_binding)
        self.assertDictContainsSubset(expected_binding, actual_binding)
    

if __name__ == '__main__':
    unittest.main()
