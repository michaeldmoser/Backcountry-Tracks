import unittest

from tptesting import fakepika

from trailhead.mq import PikaClient

class TestPikaClient(unittest.TestCase):
    def setUp(self):
        """PikaClient.connect() creates connection to RabbitMQ"""
        # This is simulating a pika.ConnectionParameters object which should
        # remain as a complete black box to the SUT
        self.connection_params = dict(host='localhost')            
        self.connection = fakepika.SelectConnectionFake()
        self.connection()

        self.client = PikaClient(self.connection, self.connection_params)

    def tearDown(self):
        pass

    def test_connection_established(self):
        '''connect() establishes a connection to RabbitMQ'''
        self.client.connect()
        self.connection.ioloop.start()
        self.assertTrue(self.connection.was_called(self.connection.__init__))

    def test_no_connection_on_instantiation(self):
        '''There should be no connection on object instantiation'''
        assert(not hasattr(self.connection, 'params'))

    def test_creates_channel(self):
        '''A channel is opened after a connect()'''
        self.client.connect()
        self.connection.ioloop.start()
        self.assertTrue(self.connection.was_called(self.connection.channel))

    def test_saves_channel(self):
        '''Saves opened channel as channel attribute'''
        self.client.connect()
        self.connection.ioloop.start()
        self.assertIsInstance(self.client.channel, fakepika.ChannelFake)

    def test_reply_queue_created(self):
        '''TrailHead() should create a reply queue for rpc requests'''
        self.client.connect()
        self.connection.ioloop.start()
        queues = self.connection.get_queues()
        self.assertGreater(len(queues), 0)

    def test_reply_queue_declaration(self):
        '''Reply queue created correctly'''
        self.client.connect()
        self.connection.ioloop.start()
        reply_queue = self.connection.get_queues()[0]
        queue = self.connection.get_queue_declaration(reply_queue)

        expected_declaration = {
                'exclusive': True,
                'durable': False,
                'auto_delete': True,
                'passive': False
                }
        self.assertDictContainsSubset(expected_declaration, queue)

    def test_reply_queue_name(self):
        '''Name saved for use by handlers'''
        self.client.connect()
        self.connection.ioloop.start()
        reply_queue = self.connection.get_queues()[0]
        self.assertEquals(reply_queue, self.client.rpc_reply)

    def test_binding_on_reply_queue(self):
        '''Should create a binding between the adventurer exchange and the reply queue'''
        self.client.connect()
        self.connection.ioloop.start()

        binding_query = {
                'exchange': 'adventurer',
                'queue': self.client.rpc_reply,
                'routing_key': 'adventurer.login.%s' % self.client.rpc_reply,
                }
        binding = self.connection.find_binding(binding_query)

        self.assertTrue(binding != dict())


if __name__ == '__main__':
    unittest.main()
