import unittest

from tptesting import environment, spy, fakepika

from groupleader.environment import Environment
from bctmessaging.connection import MessagingBuilder

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

if __name__ == '__main__':
    unittest.main()

