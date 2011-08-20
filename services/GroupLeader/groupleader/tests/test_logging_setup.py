import unittest

from tptesting import spy
from groupleader.log import Logging

class TestLoggingSetup(unittest.TestCase):

    def test_configures_logging(self):
        '''Configures logging with provided config'''
        dictconfig = spy.SpyObject()
        dictconfig()

        log = Logging(dictconfig)

        config = {
                'shouldnt': 'find me',

                'logging': {
                    'handlers': None, 'loggers': None
                    }
                }
        log(config)

        dictconfig_use = spy.UsageRecord('__call__', config['logging'])
        self.assertTrue(dictconfig.verify_usage(dictconfig_use))

if __name__ == '__main__':
    unittest.main()
        
