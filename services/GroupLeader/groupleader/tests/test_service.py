import pdb
import unittest

from tptesting import spy, environment, tplogging
from groupleader.services import Service

class TestService(unittest.TestCase):
    def setUp(self):
        self.config = {
                'option1': 'option 1 value',
                'option2': 'option 2 value',
                }

        self.EntryPoint = spy.SpyObject()
        self.Environ = spy.SpyObject()
        self.setproctitle = spy.SpyObject()
        self.setproctitle()

        self.service = Service('TestService', 'test_service', self.EntryPoint,
                self.config, self.Environ, self.setproctitle, 'Test Service')

    def test_instantiate_entry_point(self):
        '''Instantiates and entry point with the config'''
        self.service()

        use = spy.UsageRecord('__init__', self.config, self.Environ)
        self.assertTrue(self.EntryPoint.verify_usage(use))

    def test_entry_point_not_instantiated(self):
        '''Entry should not be started if start() not called'''
        self.assertFalse(self.EntryPoint.was_called('__init__'))

    def test_entry_point_not_started(self):
        '''Entry should not be started if start() not called'''
        self.assertFalse(self.EntryPoint.was_called('start'))

    def test_entry_point_started(self):
        '''The entry point gets started'''
        self.service()
        self.assertTrue(self.EntryPoint.was_called('start'))

    def test_process_title_set(self):
        '''The process name gets set'''
        self.service()
        use = spy.UsageRecord('__call__', 'GroupLeader: Test Service')
        self.assertTrue(self.setproctitle.verify_usage(use))

class TestServiceExceptions(unittest.TestCase):
    def test_entry_point_exception(self):
        '''Exceptions raise in Entry Point should be logged'''
        test_env = environment.create()
        class ExceptionTest(Exception):
            pass

        class EntryPointStub(object):
            def __init__(self, config, environ):
                pass

            def start(self):
                raise ExceptionTest

        def setproctitle_stub(title):
            pass

        self.config = {
                'option1': 'option 1 value',
                'option2': 'option 2 value',
                }

        self.Environ = spy.SpyObject()
        self.service = Service('Test', 'test', EntryPointStub, self.config,
                self.Environ, setproctitle_stub, 'process name')

        try:
            self.service()
        except ExceptionTest:
            pass

        messages = ('\n').join([log.msg for log in tplogging.logs.messages])
        self.assertIn('ExceptionTest', messages)
        


if __name__ == '__main__':
    unittest.main()

