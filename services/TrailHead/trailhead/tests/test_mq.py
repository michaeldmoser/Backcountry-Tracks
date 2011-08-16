import unittest

from pika import spec, frame
import pika
import json

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

    def test_binding_on_rpc_reply_exchange(self):
        '''Should create a binding between the rpc_reply exchange and the reply queue'''
        self.client.connect()
        self.connection.ioloop.start()

        binding_query = {
                'exchange': 'rpc_reply',
                'queue': self.client.rpc_reply,
                'routing_key': '%s' % self.client.rpc_reply,
                }
        binding = self.connection.find_binding(binding_query)

        self.assertTrue(binding != dict())

    def test_should_consume_messages_on_reply_queue(self):
        '''Needs to consume messages that are sent to the reply queue'''
        self.client.connect()
        self.connection.ioloop.start()

        self.assertTrue(self.connection.was_called(self.client.channel.basic_consume))

class TestPikaClientReplyHandling(unittest.TestCase):
    def setUp(self):
        """PikaClient.connect() creates connection to RabbitMQ"""
        # This is simulating a pika.ConnectionParameters object which should
        # remain as a complete black box to the SUT
        self.connection_params = dict(host='localhost')            
        self.connection = fakepika.SelectConnectionFake()
        self.connection()

        self.client = PikaClient(self.connection, self.connection_params)
        self.client.connect()
        self.connection.ioloop.start()

        self.received_headers = None
        self.received_body = None

        self.correlation_id = '1234'
        self.client.register_rpc_reply(self.correlation_id, self.reply_stub)

        method = frame.Method(1, spec.Basic.ConsumeOk())
        header = pika.BasicProperties(
                correlation_id = self.correlation_id,
                content_type = 'application/json'
                )
        self.message = json.dumps(dict(successful = True))
        self.client.receive_message(self.client.channel, method, header, self.message)

    def reply_stub(self, headers, body):
        self.received_headers = headers
        self.received_body = body

    def test_register_to_receive_reply(self):
        '''PikaClient.register_rpc_reply calls reply callback on correct correlation id'''
        self.assertEquals(self.received_headers.correlation_id, self.correlation_id)

    def test_register_to_receive_reply(self):
        '''PikaClient.register_rpc_reply calls reply callback on correct correlation id'''
        self.assertEquals(self.received_body, self.message)



if __name__ == '__main__':
    unittest.main()
