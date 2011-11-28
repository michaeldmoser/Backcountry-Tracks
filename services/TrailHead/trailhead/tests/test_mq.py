import unittest

from pika import spec, frame
import pika
import json

from tptesting import fakepika

from bctmessaging.remoting import RemotingClient, RemoteService
from trailhead.mq import PikaClient

class TestPikaClient(unittest.TestCase):
    def setUp(self):
        """PikaClient.connect() creates connection to RabbitMQ"""
        # This is simulating a pika.ConnectionParameters object which should
        # remain as a complete black box to the SUT
        self.connection_params = dict(host='localhost')            
        self.connection = fakepika.SelectConnectionFake()
        self.connection()

        self.client = PikaClient(self.connection, self.connection_params, RemotingClient)

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

    def test_remoting_client(self):
        '''RemotingClient usable from PikaClient'''
        self.client.connect()
        self.connection.ioloop.start()

        remote_service = RemoteService('adventurer')
        command = remote_service.login('blah', 'secret')
        self.client.remoting.call(command)

        self.assertGreater(len(self.connection.published_messages), 0)



if __name__ == '__main__':
    unittest.main()

