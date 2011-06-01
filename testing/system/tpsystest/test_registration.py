import unittest

import urllib2
import json

from tptesting import environment, utils

class TestSubmitRegistration(unittest.TestCase):
    def setUp(self):
        self.environ = environment.create()
        self.environ.make_pristine()
        self.environ.bringup_infrastructure()

        register_url = '/'.join([self.environ.trailhead_url, 'register'])
        self.register_request = urllib2.Request(register_url)

        albert = self.environ.albert
        self.register_data = {
                'first_name': albert.first_name,
                'last_name': albert.last_name,
                'email': albert.email,
                'birthdate': albert.birthdate,
                'password': albert.password,
            }
        self.register_request.add_data(json.dumps(self.register_data))
        self.albert = albert

    def tearDown(self):
        self.environ.teardown()

    def test_submit_valid_registration(self):
        """Submitting a valid registration should return successful"""
        def assert_valid_response():
            try:
                response = urllib2.urlopen(self.register_request)
            except urllib2.HTTPError, e:
                self.fail(str(e))

            status_code = response.code
            self.assertEquals(status_code, 202)

            response_data = response.read()
            self.assertEquals(len(response_data), 0)

        utils.try_until(1, assert_valid_response)

    def test_submit_valid_registration_saved(self):
        '''Submitting a valid registration should create a new user'''
        def successful_request():
            try:
                response = urllib2.urlopen(self.register_request)
            except urllib2.HTTPError:
                self.fail(str(e))
        utils.try_until(1, successful_request)

        user_bucket = self.environ.get_database('users')
        albert_user = user_bucket.get(self.albert.email)
        albert_data = albert_user.get_data()

        self.assertEquals(albert_data, self.register_data)

if __name__ == '__main__':
    unittest.main()
