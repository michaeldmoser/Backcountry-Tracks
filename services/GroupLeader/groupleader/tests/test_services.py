import unittest

from tptesting import spy

from groupleader.services import Services, ServiceBuilder, Service

class TestServices(unittest.TestCase):

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
                    'handlers': None, 'loggers': None,
                    }
                }

        class TestServiceStub(object):
            def __init__(stub, config):
                pass

            def start(fake):
                pass

        self.servicespy = spy.SpyObject()
        
        load_services = Services(self.servicespy)
        self.services = load_services(self.config)

    def test_creates_service(self):
        '''Loads a service correctly'''
        service_config = self.config['services']['TestService/test_service']
        use = spy.UsageRecord('__init__', 'TestService', 'test_service', service_config)

        self.assertTrue(self.servicespy.verify_usage(use))

    def test_spawns_the_service(self):
        '''Spawns the service'''
        self.services.spawn()
        self.assertTrue(self.servicespy.was_called('start'))

    def test_not_spawned(self):
        '''Service should not be spawned yet'''
        self.assertFalse(self.servicespy.was_called('start'))

class TestServiceBuilder(unittest.TestCase):

    def setUp(self):
        class TestEntryPoint(object):
            def __init__(stub, config):
                pass

            def start(stub):
                pass
        self.TestEntryPoint = TestEntryPoint

        def load_entry_point(dist, group, name):
            return TestEntryPoint
        self.load_entry_point = spy.SpyObject(load_entry_point)
        self.load_entry_point()


        self.servicespy = spy.SpyObject()
        self.ProcessSpy = spy.SpyObject() 
        self.Environ = spy.SpyObject()
        self.Environ()

        self.setproctitle = spy.SpyObject()
        self.setproctitle()

        self.dist = 'TestService'
        self.name = 'test'
        self.group =  'tripplanner.service'

        builder = ServiceBuilder(self.load_entry_point, self.group,
                self.servicespy, self.ProcessSpy, self.Environ, self.setproctitle)
        self.service_config = {'test': 'config'}
        self.service = builder(self.dist, self.name, self.service_config)

    def test_load_entry_point(self):
        '''Load a services entry point'''
        use = spy.UsageRecord('__call__', self.dist, self.group, self.name)
        self.assertTrue(self.load_entry_point.verify_usage(use))

    def test_returns_service(self):
        '''Returns a service'''
        self.assertIs(self.service, self.ProcessSpy)

    def test_service_created(self):
        '''Service creation'''
        use = spy.UsageRecord('__init__', self.TestEntryPoint, self.service_config,
                self.Environ, self.setproctitle)
        self.assertTrue(self.servicespy.verify_usage(use))

    def test_process_target(self):
        '''Process should have service as target'''
        use = spy.UsageRecord('__init__', target=self.servicespy)
        self.assertTrue(self.service.verify_usage(use))


if __name__ == '__main__':
    unittest.main()

