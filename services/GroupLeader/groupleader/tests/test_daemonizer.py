import unittest

import signal

from tptesting import fakedaemonizer

from groupleader.daemonizer import Daemonizer

class TestGroupLeaderDaemonizer(unittest.TestCase):

    def setUp(self):
        def sigterm_handler(signum, stack):
            pass
        self.sigterm_handler = sigterm_handler
        self.fakedaemon = fakedaemonizer.Daemonizer()
        daemon = Daemonizer(self.fakedaemon, fakedaemonizer.PidFile)

        self.path = '/var/run/tripplanner/groupleader.pid'
        self.context = daemon(self.path, sigterm_handler)

    def test_uses_pidfile(self):
        '''Daemonizer should use the configure pidfile'''
        self.assertEquals(self.path, self.fakedaemon.pidfile.path)

    def test_returns_context_class_instance(self):
        '''Should return an instance of the context class'''
        self.assertIsInstance(self.context, fakedaemonizer.Daemonizer)

    def test_signal_map(self):
        '''Should provide a sigterm handler'''
        expected_sig_map = {
                signal.SIGTTIN: None,
                signal.SIGTTOU: None,
                signal.SIGTSTP: None,
                signal.SIGTERM: self.sigterm_handler
                }

        self.assertEquals(expected_sig_map, self.context.signal_map)


if __name__ == '__main__':
    unittest.main()

