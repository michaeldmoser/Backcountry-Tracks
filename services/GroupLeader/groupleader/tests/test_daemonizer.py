import unittest

from tptesting import fakedaemonizer

from groupleader.daemonizer import Daemonizer

class TestGroupLeaderDaemonizer(unittest.TestCase):

    def setUp(self):
        self.fakedaemon = fakedaemonizer.Daemonizer()
        daemon = Daemonizer(self.fakedaemon, fakedaemonizer.PidFile)

        self.path = '/var/run/tripplanner/groupleader.pid'
        self.context = daemon(self.path)

    def test_uses_pidfile(self):
        '''Daemonizer should use the configure pidfile'''
        self.assertEquals(self.path, self.fakedaemon.pidfile.path)

    def test_returns_context_class_instance(self):
        '''Should return an instance of the context class'''
        self.assertIsInstance(self.context, fakedaemonizer.Daemonizer)

if __name__ == '__main__':
    unittest.main()

