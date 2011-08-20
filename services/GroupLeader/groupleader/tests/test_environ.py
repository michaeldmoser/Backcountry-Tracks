import unittest

from tptesting import environment, spy, fakepika

from groupleader.environment import Environment, MessagingBuilder

class TestGroupLeaderEnviron(unittest.TestCase):

    def test_build_messaging(self):
        '''Builds a messaging channel'''
        test_environ = environment.create()
        messagingspy = spy.SpyObject()
        messagingspy()

        class StubCallback(object):
            pass

        environ = Environment(test_environ.mock_config, messagingspy)
        environ.open_messaging_channel(StubCallback)

        use = spy.UsageRecord('__call__', StubCallback)
        self.assertTrue(messagingspy.verify_usage(use))

class TestEnvironMessagingBuilder(unittest.TestCase):
    def setUp(self):
        self.environ = environment.create()
        self.pikaspy = fakepika.SelectConnectionFake()
        self.paramspy = spy.SpyObject()

        class MessagingBuilderSUT(MessagingBuilder):
            def _MessagingBuilder__pika_connection(sut):
                return self.pikaspy, self.paramspy

        self.messaging = MessagingBuilderSUT(self.environ.mock_config)

        self.callbackspy = spy.SpyObject()
        self.messaging(self.callbackspy.on_channel_callback)

    def test_opening_channel(self):
        '''Creates a channel and passes it to the callback'''
        usage = self.callbackspy.usage[0]
        self.assertIsInstance(usage.args[0], fakepika.ChannelFake)

    def test_connection_params(self):
        '''Connection parameters from config used'''
        self.assertEquals(self.paramspy.usage[0].kwargs, 
                self.environ.mock_config['messaging']['connection_params'])


if __name__ == '__main__':
    unittest.main()

