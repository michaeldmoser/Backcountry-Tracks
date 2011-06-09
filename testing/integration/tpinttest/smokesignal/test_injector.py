import unittest

from tptesting import environment
import pika

from smokesignal.injector import smokesignal

class TestInjector(unittest.TestCase):
    @classmethod 
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.smokesignalapp = smokesignal()

    @classmethod
    def tearDownClass(cls):
        cls.environ.teardown()

    def test_uses_pika_connection(self):
        '''Uses pika connection object'''
        pika_dependency = self.smokesignalapp.pika_connection
        self.assertIsInstance(pika_dependency, pika.BlockingConnection)


if __name__ == '__main__':
    unittest.main()

