import unittest

import yaml

from tptesting import fakepika, fakedaemonizer, spy

from groupleader.controller import GroupLeader

class TestGroupLeaderRun(unittest.TestCase):

    def setUp(self):
        self.config = {
                'services': {
                    'TestService/test_service': {
                            'option1': '1',
                            'option2': '2'
                        }
                    },

                'messaging': {
                    'connection_params': {
                            'host': 'localhost',
                            'virtual_host': '/'
                        }
                    },
                'pidfile': '/var/run/tripplanner/groupleader.pid',

                'logging': {
                    'handlers': None,
                    'loggers': None,
                    'formaters': None
                    }
                }

        def daemonizer__call__(pidfile, shutdown):
            return fakedaemonizer.Daemonizer()
        self.daemonizer = spy.SpyObject(daemonizer__call__)
        self.daemonizer()

        self.serviceloader = spy.SpyObject()
        self.loggingspy = spy.SpyObject()
        self.setproctitle = spy.SpyObject()
        self.setproctitle()

        self.pidlockfile = spy.SpyObject()
        def kill_stub(self, pid, signal):
                pass

        self.gl = GroupLeader(self.config, self.daemonizer, self.loggingspy, 
                self.serviceloader, self.setproctitle, self.pidlockfile, kill_stub)
        self.gl.run()


    def test_daemon_context_use(self):
        '''GroupLeader sets the correct pidfile'''
        pidfile_use = spy.UsageRecord('__call__', self.config['pidfile'], self.gl.shutdown)
        self.assertTrue(self.daemonizer.verify_usage(pidfile_use))

    def test_setups_logging(self):
        '''GroupLeader should setup logging facilities'''
        logging_use = spy.UsageRecord('__init__', self.config)
        self.assertTrue(self.loggingspy.verify_usage(logging_use))

    def test_loads_the_services(self):
        '''GroupLeader loads the configured services'''
        serviceloader_use = spy.UsageRecord('__init__', self.config)
        self.assertTrue(self.serviceloader.verify_usage(serviceloader_use))

    def test_spawn_service_processes(self):
        '''GroupLeader spawn processes for the services'''
        self.assertTrue(self.serviceloader.services_spawned)

    def test_sets_process_title(self):
        '''Sets the process title'''
        use = spy.UsageRecord('__call__', 'GroupLeader: master')
        self.assertTrue(self.setproctitle.verify_usage(use))

class TestGroupLeaderStop(unittest.TestCase):

    def test_stops_all_services(self):
        '''Stops all groupleader services'''
        self.config = {
                'services': {
                    'TestService/test_service': {
                            'option1': '1',
                            'option2': '2'
                        }
                    },

                'messaging': {
                    'connection_params': {
                            'host': 'localhost',
                            'virtual_host': '/'
                        }
                    },
                'pidfile': '/var/run/tripplanner/groupleader.pid',

                'logging': {
                    'handlers': None,
                    'loggers': None,
                    'formaters': None
                    }
                }

        def daemonizer__call__(pidfile):
            return fakedaemonizer.Daemonizer()
        self.daemonizer = spy.SpyObject(daemonizer__call__)
        self.daemonizer()

        self.serviceloader = spy.SpyObject()
        self.loggingspy = spy.SpyObject()
        self.setproctitle = spy.SpyObject()
        self.setproctitle()

        self.kill = spy.SpyObject()
        self.kill()

        class PidLockFileStub(object):
            def read_pid(self):
                return '1234'

        self.gl = GroupLeader(self.config, self.daemonizer, self.loggingspy, 
                self.serviceloader, self.setproctitle, PidLockFileStub(), self.kill)
        self.gl.stop()

        import signal
        use = spy.UsageRecord('__call__', 1234, signal.SIGTERM)
        self.assertTrue(self.kill.verify_usage(use))

class TestGroupLeaderShutdown(unittest.TestCase):

    def test_shutdown_all_services(self):
        '''Terminate all of the child processes'''
        self.config = {
                'services': {
                    'TestService/test_service': {
                            'option1': '1',
                            'option2': '2'
                        }
                    },

                'messaging': {
                    'connection_params': {
                            'host': 'localhost',
                            'virtual_host': '/'
                        }
                    },
                'pidfile': '/var/run/tripplanner/groupleader.pid',

                'logging': {
                    'handlers': None,
                    'loggers': None,
                    'formaters': None
                    }
                }

        def daemonizer__call__(pidfile, shutdown):
            return fakedaemonizer.Daemonizer()
        self.daemonizer = spy.SpyObject(daemonizer__call__)
        self.daemonizer()

        self.serviceloader = spy.SpyObject()
        self.loggingspy = spy.SpyObject()
        self.setproctitle = spy.SpyObject()
        self.setproctitle()

        self.pidlockfile = spy.SpyObject()
        def kill_stub(self, pid, signal):
                pass

        self.gl = GroupLeader(self.config, self.daemonizer, self.loggingspy, 
                self.serviceloader, self.setproctitle, self.pidlockfile, kill_stub)
        self.gl.run()

        self.gl.shutdown(1234, [])

        self.assertTrue(self.serviceloader.was_called('shutdown'))

if __name__ == '__main__':
    unittest.main()

