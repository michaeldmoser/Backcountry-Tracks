import unittest
import subprocess
import json

from urllib2 import urlopen, URLError, HTTPError, Request

from tptesting import environment, utils

class TestRegisterHandler(unittest.TestCase):
    def setUp(self):
        self.environ = environment.create()
        self.environ.make_pristine()

        self.environ.rabbitmq.start()
        self.environ.start_trailhead()

    def tearDown(self):
        self.environ.teardown()

    def test_slash_register_exists(self):
        """Register url exists"""
        hostname = self.environ.hostname
        app_url_prefix = self.environ.url_prefix
        url = 'http://%s:8080/%s/register' % (hostname, app_url_prefix)
        def assert_port_accessable():
            try:
                urlopen(url)
            except HTTPError, e:
                self.assertEquals(405, e.code)
            except URLError, e:
                self.fail(str(e))

        utils.try_until(1, assert_port_accessable)

    def test_can_post_to_register(self):
        '''Can post data to /app/register'''
        hostname = self.environ.hostname
        app_url_prefix = self.environ.url_prefix
        url = 'http://%s:8080/%s/register' % (hostname, app_url_prefix)

        register_request = Request(url)
        albert = self.environ.albert
        register_data = {
                'first_name': albert.first_name,
                'last_name': albert.last_name,
                'email': albert.email,
                'birthdate': albert.birthdate,
                'password': albert.password,
            }
        register_request.add_data(json.dumps(register_data))

        def assert_port_accessable():
            try:
                urlopen(register_request)
            except URLError, e:
                self.fail(str(e))

        utils.try_until(1, assert_port_accessable)

if __name__ == '__main__':
    unittest.main()

