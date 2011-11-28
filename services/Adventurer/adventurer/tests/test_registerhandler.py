import unittest

import json

from tptesting import faketornado, fakepika, environment, thandlers

from tornado.web import RequestHandler
from trailhead.mq import PikaClient
from trailhead.tests.utils import setup_handler

from adventurer.register import RegisterHandler, ActivateHandler

class TestRegisterHandlerPost(thandlers.TornadoHandlerTestCase):

    def request_handler(self):
        return RegisterHandler

    def url(self):
        return '/app/register'

    def active_user(self):
        return None

    def method(self):
        return 'POST'

    def method_args(self):
        return list(), dict()

    def rpc_result(self):
        return {'successful': True}

    def http_response(self):
        return self.rpc_result()

    def expected_rpc_request(self):
        registration = dict(self.environ.albert)
        return 'register', registration

    def expected_durability(self):
        return True

    def remote_service_name(self):
        return 'Adventurer'

    def http_request_body(self):
        return json.dumps(self.environ.albert)

class TestRegisterHandlerHttp(unittest.TestCase):

    def test_returned_status_code_400(self):
        """On a bad post should return a 400 bad data status code"""
        headers = {'Content-Type': 'mulitpart/form-data'}
        handler, application, pika = setup_handler(RegisterHandler, 'POST',
                '/app/register', headers = headers)
        handler.post()

        self.assertEquals(handler._status_code, 400)

class TestActivateHandler(thandlers.TornadoHandlerTestCase):

    def setUp(self):
        self.activate_code = '1234'
        thandlers.TornadoHandlerTestCase.setUp(self)

    def request_handler(self):
        return ActivateHandler

    def url(self):
        return '/app/activate/%s/%s' % (self.environ.douglas.email, self.activate_code)

    def active_user(self):
        return None

    def method(self):
        return 'GET'

    def method_args(self):
        return [self.environ.douglas.email, self.activate_code], dict()

    def rpc_result(self):
        return {'successful': True}

    def http_response(self):
        return ''

    def expected_rpc_request(self):
        registration = self.method_args()
        return 'activate', registration[0]

    def expected_durability(self):
        return True

    def remote_service_name(self):
        return 'Adventurer'

    def http_request_body(self):
        return None

    def http_status_code(self):
        return 303


if __name__ == '__main__':
    unittest.main()

