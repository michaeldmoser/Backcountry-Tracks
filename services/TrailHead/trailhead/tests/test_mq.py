import unittest

from trailhead.mq import PikaClient

class TestPikaClient(unittest.TestCase):
    def setUp(self):
        """PikaClient.connect() creates connection to RabbitMQ"""
        class PikaChannelStub(object):
            pass
        self.pikachannel = PikaChannelStub

        class PikaConnectionFake(object):
            def __call__(fake, params, on_open_callback=None):
                fake.params = params
                fake.on_open_callback = on_open_callback
                on_open_callback(fake)

                return fake

            def channel(fake, callback=None):
                fake.channel_opened = True
                if callback is not None:
                    callback(PikaChannelStub())

        # This is simulating a pika.ConnectionParameters object which should
        # remain as a complete black box to the SUT
        self.connection_params = dict(host='localhost')            
        self.connection = PikaConnectionFake()

        self.client = PikaClient(self.connection, self.connection_params)

    def tearDown(self):
        pass

    def test_connection_established(self):
        '''connect() establishes a connection to RabbitMQ'''
        self.client.connect()
        self.assertEquals(self.connection_params, self.connection.params)

    def test_no_connection_on_instantiation(self):
        '''There should be no connection on object instantiation'''
        assert(not hasattr(self.connection, 'params'))

    def test_creates_channel(self):
        '''A channel is opened after a connect()'''
        self.client.connect()
        assert(self.connection.channel_opened)

    def test_saves_channel(self):
        '''Saves opened channel as channel attribute'''
        self.client.connect()
        assert(isinstance(self.client.channel, self.pikachannel))






if __name__ == '__main__':
    unittest.main()
