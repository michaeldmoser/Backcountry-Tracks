import unittest
import subprocess
import json

from urllib2 import urlopen, URLError, HTTPError, Request

from tptesting import environment, utils

class TestRegisterHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.rabbitmq.start_server()

        cls.environ.nginx.start()
        cls.environ.start_trailhead()

        cls.register_url = '/'.join([cls.environ.trailhead_url, 'register'])

        cls.register_request = Request(
                url = cls.register_url,
                data = json.dumps(cls.environ.albert),
                headers = {
                    'Content-Type': 'application/json'
                    }
                )

    @classmethod
    def tearDownClass(cls):
        cls.environ.teardown()

    def test_slash_register_exists(self):
        """Register url exists"""
        def assert_port_accessable():
            try:
                urlopen(self.register_url)
            except HTTPError, e:
                self.assertEquals(405, e.code)
            except URLError, e:
                self.fail(str(e))

        utils.try_until(1, assert_port_accessable)

    def test_can_post_to_register(self):
        '''Can post data to /app/register'''
        def assert_port_accessable():
            try:
                urlopen(self.register_request)
            except URLError, e:
                self.fail(str(e))

        utils.try_until(1, assert_port_accessable)


    def test_accepts_json_mime_type(self):
        '''Should accept a content-type of application/json'''
        response = urlopen(self.register_request)

        status_code = response.code
        self.assertEquals(status_code, 202)

    def test_rejects_non_json_mime_type(self):
        '''Should reject content-types that are no application/json'''
        register_request = Request(
                url = self.register_url,
                data = json.dumps(self.environ.albert),
                headers = {
                    'Content-Type': 'multipart/form-data'
                    }
                )

        with self.assertRaises(HTTPError) as httperror:
            response = urlopen(register_request)

        self.assertEquals(httperror.exception.code, 400)

if __name__ == '__main__':
    unittest.main()

