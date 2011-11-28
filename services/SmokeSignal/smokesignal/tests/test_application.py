import unittest

from tptesting import fakepika
from smokesignal.application import SmokeSignalApp

class TestSmokeSignalConfiguration(unittest.TestCase):
    def setUp(self):
        self.pika_class = fakepika.BlockingConnectionFake()
        pika_connection = self.pika_class()

        self.config = {
                'exchanges': [
                    {
                        'exchange': 'some_random_rpc',
                        'durable': True,
                        'type': 'topic',
                        },
                    {
                        'exchange': 'random',
                        'durable': False,
                        'type': 'direct',
                        }
                    ],
                'queues': [
                    {
                        'queue': 'random_rpc',
                        'durable': True,
                        },
                    {
                        'queue': 'random_user_rpc',
                        'durable': True,
                        },
                    {
                        'queue': 'activation_rpc',
                        'durable': False,
                        'exclusive': True,
                        'auto_delete': True,
                        },
                    ],
                'bindings': [
                    {
                        'exchange': 'some_random_rpc',
                        'queue': 'random_rpc',
                        'routing_key': 'rpc.adventurer',
                        },
                    {
                        'exchange': 'random',
                        'queue': 'random_user_rpc',
                        'routing_key': 'rpc.gear',
                        },
                    ]
                }

        app = SmokeSignalApp(pika_connection, self.config)
        app.run()

    def test_some_random_rpc_exchange(self):
        '''some_random_rpc exchange declared with configuration'''
        expected_exchange_declare = {
            'type': 'topic',
            'durable': True,
            'auto_delete': False,
            'internal': False,
            'arguments': {}
            }
        actual_exchange = self.pika_class.get_exchange_declaration('some_random_rpc')
        self.assertDictContainsSubset(expected_exchange_declare, actual_exchange)

    def test_random_exchange(self):
        '''random exchange declared with configuration'''
        expected_exchange_declare = {
            'type': 'direct',
            'durable': False,
            'auto_delete': False,
            'internal': False,
            'arguments': {}
            }
        actual_exchange = self.pika_class.get_exchange_declaration('random')
        self.assertDictContainsSubset(expected_exchange_declare, actual_exchange)

    def test_random_rpc_qeue(self):
        '''The random_rpc queue is declared with correct configuration'''
        expected_queue_declare = {
            'durable': True,
            'auto_delete': False,
            'arguments': {}
            }
        actual_queue = self.pika_class.get_queue_declaration('random_rpc')
        self.assertDictContainsSubset(expected_queue_declare, actual_queue)

    def test_random_user_rpc_qeue(self):
        '''The random_user_rpc queue is declared with correct configuration'''
        expected_queue_declare = {
            'durable': True,
            'auto_delete': False,
            'arguments': {}
            }
        actual_queue = self.pika_class.get_queue_declaration('random_user_rpc')
        self.assertDictContainsSubset(expected_queue_declare, actual_queue)

    def test_activation_rpc_qeue(self):
        '''The activation_rpc queue is declared with correct configuration'''
        expected_queue_declare = {
            'durable': False,
            'auto_delete': True,
            'exclusive': True,
            'arguments': {}
            }
        actual_queue = self.pika_class.get_queue_declaration('activation_rpc')
        self.assertDictContainsSubset(expected_queue_declare, actual_queue)

    def test_rpc_adventurer_binding(self):
        '''The rpc.adventurer binding is created'''
        search_binding = self.config['bindings'][0]
        actual_binding = self.pika_class.find_binding(search_binding)
        self.assertDictContainsSubset(search_binding, actual_binding)

    def test_rpc_gear_binding(self):
        '''The rpc.gear binding is created'''
        search_binding = self.config['bindings'][1]
        actual_binding = self.pika_class.find_binding(search_binding)
        self.assertDictContainsSubset(search_binding, actual_binding)

class TestSmokeSignalRPCReply(unittest.TestCase):
    def setUp(self):
        self.pika_class = fakepika.BlockingConnectionFake()
        pika_connection = self.pika_class()

        app = SmokeSignalApp(pika_connection)
        app.run()

    def notest_creates_exchange(self):
        '''Creates the registration exchange'''
        expected_exchange_declare = {
            'type': 'topic',
            'durable': True,
            'auto_delete': False,
            'internal': False,
            'arguments': {}
            }
        actual_exchange = self.pika_class.get_exchange_declaration('rpc_reply')
        self.assertDictContainsSubset(expected_exchange_declare, actual_exchange)

class TestSmokeSignalAppRegistration(unittest.TestCase):
    def setUp(self):
        self.pika_class = fakepika.BlockingConnectionFake()
        pika_connection = self.pika_class()

        app = SmokeSignalApp(pika_connection)
        app.run()

    def notest_creates_rpc_exchange(self):
        '''Creates the rpc exchange'''
        expected_exchange_declare = {
            'type': 'topic',
            'durable': True,
            'auto_delete': False,
            'internal': False,
            'arguments': {}
            }
        actual_exchange = self.pika_class.get_exchange_declaration('rpc')
        self.assertDictContainsSubset(expected_exchange_declare, actual_exchange)

    def notest_creates_exchange(self):
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

    def notest_creates_queue(self):
        '''Creates the register queue'''
        expected_queue_declare = {
            'durable': True,
            'auto_delete': False,
            'arguments': {}
            }
        actual_queue = self.pika_class.get_queue_declaration('register_rpc')
        self.assertDictContainsSubset(expected_queue_declare, actual_queue)

    def notest_creates_binding(self):
        '''Creates the exchange<->queue binding'''
        expected_binding = {
            'queue': 'register_rpc',
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

    def notest_creates_exchange(self):
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

    def notest_creates_queue(self):
        '''Creates the login queue'''
        expected_queue_declare = {
            'durable': True,
            'auto_delete': False,
            'arguments': {}
            }
        actual_queue = self.pika_class.get_queue_declaration('login_rpc')
        self.assertDictContainsSubset(expected_queue_declare, actual_queue)

    def notest_creates_binding(self):
        '''Creates the exchange<->queue binding'''
        expected_binding = {
            'queue': 'login_rpc',
            'exchange': 'adventurer',
            'routing_key': 'adventurer.login',
            }
        actual_binding = self.pika_class.find_binding(expected_binding)
        self.assertDictContainsSubset(expected_binding, actual_binding)

class TestSmokeSignalGear(unittest.TestCase):
    def setUp(self):
        self.pika_class = fakepika.BlockingConnectionFake()
        pika_connection = self.pika_class()

        app = SmokeSignalApp(pika_connection)
        app.run()

    def notest_gear_exchange(self):
        '''Creates an exchange for Gear related messages'''
        expected_exchange_declare = {
            'type': 'topic',
            'durable': True,
            'auto_delete': False,
            'internal': False,
            'arguments': {}
            }
        actual_exchange = self.pika_class.get_exchange_declaration('gear')
        self.assertDictContainsSubset(expected_exchange_declare, actual_exchange)

    def notest_user_gear_rpc_queue(self):
        '''Creates the user_gear_rpc queue'''
        expected_queue_declare = {
            'durable': True,
            'auto_delete': False,
            'arguments': {}
            }
        actual_queue = self.pika_class.get_queue_declaration('user_gear_rpc')
        self.assertDictContainsSubset(expected_queue_declare, actual_queue)

    def notest_creates_binding(self):
        '''Creates the exchange<->queue binding for user gear RPCs'''
        expected_binding = {
            'queue': 'user_gear_rpc',
            'exchange': 'gear',
            'routing_key': 'gear.user.rpc',
            }
        actual_binding = self.pika_class.find_binding(expected_binding)
        self.assertDictContainsSubset(expected_binding, actual_binding)

class TestSmokeSignalAdventurerRPC(unittest.TestCase):
    def setUp(self):
        self.pika_class = fakepika.BlockingConnectionFake()
        pika_connection = self.pika_class()

        app = SmokeSignalApp(pika_connection)
        app.run()

    def notest_adventurer_rpc_queue(self):
        '''Creates the user_gear_rpc queue'''
        expected_queue_declare = {
            'durable': True,
            'auto_delete': False,
            'arguments': {}
            }
        actual_queue = self.pika_class.get_queue_declaration('adventurer_rpc')
        self.assertDictContainsSubset(expected_queue_declare, actual_queue)

    def notest_creates_binding(self):
        '''Creates the exchange<->queue binding for adventurer RPCs'''
        expected_binding = {
            'queue': 'adventurer_rpc',
            'exchange': 'adventurer',
            'routing_key': 'adventurer.rpc',
            }
        actual_binding = self.pika_class.find_binding(expected_binding)
        self.assertDictContainsSubset(expected_binding, actual_binding)
    
class TestSmokeSignalTrips(unittest.TestCase):
    def setUp(self):
        self.pika_class = fakepika.BlockingConnectionFake()
        pika_connection = self.pika_class()

        app = SmokeSignalApp(pika_connection)
        app.run()

    def notest_trips_exchange(self):
        '''Creates an exchange for Trips related messages'''
        expected_exchange_declare = {
            'type': 'topic',
            'durable': True,
            'auto_delete': False,
            'internal': False,
            'arguments': {}
            }
        actual_exchange = self.pika_class.get_exchange_declaration('trips')
        self.assertDictContainsSubset(expected_exchange_declare, actual_exchange)

    def notest_user_trips_rpc_queue(self):
        '''Creates the user_trips_rpc queue'''
        expected_queue_declare = {
            'durable': True,
            'auto_delete': False,
            'arguments': {}
            }
        actual_queue = self.pika_class.get_queue_declaration('trips_rpc')
        self.assertDictContainsSubset(expected_queue_declare, actual_queue)

    def notest_creates_binding(self):
        '''Creates the exchange<->queue binding for user trips RPCs'''
        expected_binding = {
            'queue': 'trips_rpc',
            'exchange': 'trips',
            'routing_key': 'trips.rpc',
            }
        actual_binding = self.pika_class.find_binding(expected_binding)
        self.assertDictContainsSubset(expected_binding, actual_binding)

if __name__ == '__main__':
    unittest.main()
