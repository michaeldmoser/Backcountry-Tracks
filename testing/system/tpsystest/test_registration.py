import unittest

import urllib2
import json

from tptesting import environment, utils

class TestSubmitRegistration(unittest.TestCase):
    def setUp(self):
        self.environ = environment.create()
        self.environ.make_pristine()
        self.environ.bringup_infrastructure()

    def tearDown(self):
        self.environ.teardown()

    def test_submit_valid_registration(self):
        """Submitting a valid registration should return successful"""

        register_url = '/'.join([self.environ.trailhead_url, 'register'])
        register_request = urllib2.Request(register_url)

        albert = self.environ.albert
        register_data = {
                'first_name': albert.first_name,
                'last_name': albert.last_name,
                'email': albert.email,
                'birthdate': albert.birthdate,
                'password': albert.password,
            }
        register_request.add_data(json.dumps(register_data))

        def assert_valid_response():
            try:
                response = urllib2.urlopen(register_request)
            except urllib2.HTTPError, e:
                self.fail(str(e))

            status_code = response.code
            self.assertEquals(status_code, 202)

            response_data = json.loads(response.read())
            self.assertEquals(len(response_data), 0)

        utils.try_until(1, assert_valid_response)

        
if __name__ == '__main__':
    unittest.main()
