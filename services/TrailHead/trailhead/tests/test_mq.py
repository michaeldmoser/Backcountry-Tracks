import unittest

from trailhead.mq import PikaClient

class TestPikaClient(unittest.TestCase):
    def setUp(self):
        """PikaClient.connect() creates connection to RabbitMQ"""
        class PikaConnectionFake(object):
            def __call__(fake, params, on_open_callback=None):
                fake.params = params
                fake.on_open_callback = on_open_callback

                return fake

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



if __name__ == '__main__':
    unittest.main()
