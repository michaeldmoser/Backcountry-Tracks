import unittest

import yaml

from tptesting import fakepika, fakedaemonizer, spy

from groupleader.controller import GroupLeader

class TestGroupLeaderProcessStart(unittest.TestCase):

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

        def daemonizer__call__(pidfile):
            return fakedaemonizer.Daemonizer()
        self.daemonizer = spy.SpyObject(daemonizer__call__)
        self.daemonizer()

        self.serviceloader = spy.SpyObject()
        self.loggingspy = spy.SpyObject()

        gl = GroupLeader(self.config, self.daemonizer, self.loggingspy, 
                self.serviceloader)
        gl.run()


    def test_pidfile_used(self):
        '''GroupLeader sets the correct pidfile'''
        pidfile_use = spy.UsageRecord('__call__', self.config['pidfile'])
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

if __name__ == '__main__':
    unittest.main()

