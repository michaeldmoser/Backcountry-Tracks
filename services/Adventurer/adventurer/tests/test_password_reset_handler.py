import unittest

import json
import uuid

from tptesting import faketornado, fakepika, environment, thandlers

from tornado.web import RequestHandler
from trailhead.mq import PikaClient
from trailhead.tests.utils import setup_handler

from adventurer.passwordreset import PasswordResetHandler

class TestPasswordResetPost(thandlers.TornadoHandlerTestCase):

    def request_handler(self):
        return PasswordResetHandler

    def url(self):
        return '/app/password'

    def active_user(self):
        return None

    def method(self):
        return 'POST'

    def method_args(self):
        return list(), dict()

    def rpc_result(self):
        return True

    def http_response(self):
        return {'reset': True}

    def expected_rpc_request(self):
        return 'reset_password', [self.environ.albert.email]

    def expected_durability(self):
        return True

    def remote_service_name(self):
        return 'Adventurer'

    def http_request_body(self):
        return json.dumps({'reset': True, 'email': self.environ.albert.email})


class TestPasswordResetGET(thandlers.TornadoHandlerTestCase):

    def handler_setup(self):
        self.reset_key = str(uuid.uuid4())

    def request_handler(self):
        return PasswordResetHandler

    def url(self):
        return '/app/password/' + self.reset_key

    def active_user(self):
        return None

    def method(self):
        return 'GET'

    def method_args(self):
        return [self.reset_key], dict()

    def rpc_result(self):
        return True

    def expected_rpc_request(self):
        return 'validate_reset_key', [self.reset_key]

    def expected_durability(self):
        return True

    def remote_service_name(self):
        return 'Adventurer'

    @property
    def http_content_type(self):
        return 'text/html'

    def test_response(self):
        headers, body = self.request._output.split('\r\n\r\n')
        self.assertIn(self.reset_key, body)


if __name__ == '__main__':
    unittest.main()

