import unittest
import urllib2
import json
import pika

from urllib2 import HTTPError


from tptesting import environment, utils

from bctmessaging.remoting import RemoteService

class TestMessagingExceptions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        environ = environment.create()
        environ.make_pristine()
        environ.bringup_infrastructure()

        cls.env = environ

        ramona = environ.ramona
        environ.create_user(ramona)
        cls.login_session = ramona.login()

        environ.riak.stop()

    def test_500_server_error(self):
        '''An exception in the backend should generate an HTTP 500 status'''
        with self.assertRaises(HTTPError) as error:
            self.login_session.open(self.env.trailhead_url + "/trips")
        exception = error.exception

        self.assertEquals(exception.code, 500)

    def test_error_message(self):
        '''HTTP 500 status should contain a message'''
        with self.assertRaises(HTTPError) as error:
            self.login_session.open(self.env.trailhead_url + "/trips")
        exception = error.exception

        self.assertGreater(exception.headers['X-Error-Message'], 4)

if __name__ == '__main__':
    unittest.main()

