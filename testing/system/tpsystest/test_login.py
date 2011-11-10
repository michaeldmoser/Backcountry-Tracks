import unittest
import urllib2
import json
import threading
import time
from urllib2 import HTTPError

import pika
from pika import spec

from tptesting import environment, utils

class TestLoginInvalidHTTPResponse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()

        cls.douglas = cls.environ.douglas
        cls.douglas.mark_registered()
        cls.environ.create_user(cls.douglas)

        cls.login_url = cls.environ.trailhead_url + '/login'

        credentials = {
                'email': cls.douglas.email,
                'password': "bad_password",
                }
        login_request = urllib2.Request(
                cls.login_url,
                json.dumps(credentials),
                headers = {'Content-Type': 'application/json'}
                )
        try:
            cls.response = urllib2.urlopen(login_request)
        except HTTPError, e:
            cls.response = e

        response_data = cls.response.read()
        cls.redirect_to = json.loads(response_data)

    def tearDown(self):
        self.environ.teardown()

    def test_send_invalid_login_response(self):
        '''Receiving an invalid login response provides location to login page'''
        expected_redirect = {"location": "/app/login"}
        self.assertEquals(self.redirect_to, expected_redirect)

    def test_http_status_code(self):
        '''Invalid login HTTP response code should be 403'''
        self.assertEquals(403, self.response.code)

class TestValidLoginHTTPResponse(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()

        cls.douglas = cls.environ.douglas
        cls.douglas.mark_registered()
        cls.environ.create_user(cls.douglas)

        cls.login_url = cls.environ.trailhead_url + '/login'

    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()

        cls.douglas = cls.environ.douglas
        cls.douglas.mark_registered()
        cls.environ.create_user(cls.douglas)

        cls.login_url = cls.environ.trailhead_url + '/login'

        credentials = {
                'email': cls.douglas.email,
                'password': cls.douglas.password,
                }
        login_request = urllib2.Request(
                cls.login_url,
                json.dumps(credentials),
                headers = {'Content-Type': 'application/json'}
                )
        
        cls.response = urllib2.urlopen(login_request)

        response_data = cls.response.read()
        cls.redirect_to = json.loads(response_data)

    def test_send_valid_login_response(self):
        '''Receiving a valid login response provides location to home page'''
        expected_redirect = {"location": "/app/home"}
        self.assertEquals(self.redirect_to, expected_redirect)

    def test_http_status_code(self):
        '''Valid login HTTP response code should be 202'''
        self.assertEquals(202, self.response.code)


if __name__ == '__main__':
    unittest.main()

