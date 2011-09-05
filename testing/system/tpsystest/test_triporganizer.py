import unittest

import urllib2
import json

from tptesting import environment, utils

class AddATrip(unittest.TestCase):
    '''Create a new trip'''

    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()

        cls.ramona = cls.environ.ramona
        cls.environ.create_user(cls.ramona)
        login_session = cls.ramona.login()

        cls.trip_data = cls.environ.trips[0] 
        trip_url = cls.environ.trailhead_url + "/trips"
        create_request = urllib2.Request(
                trip_url,
                data=json.dumps(cls.trip_data)
                )

        cls.create_response = login_session.open(create_request)
        body = cls.create_response.read()
        cls.response_body = json.loads(body)

    def test_trip_data_returned(self):
        '''Should return the trip data'''
        self.assertDictContainsSubset(self.trip_data, self.response_body)

    def test_trip_owner(self):
        '''The trip owner should be part of the returned data'''
        self.assertEquals(self.ramona.email, self.response_body['owner'])

    def test_trip_id(self):
        '''The response body should have an id listed'''
        self.assertIn('id', self.response_body)

    def test_trip_in_database(self):
        '''Make sure the trip is in the database'''
        bucket = self.environ.riak.get_database(self.environ.buckets['trips'])
        keys = bucket.get_keys()
        doc_object = bucket.get(str(keys[0]))
        trip = doc_object.get_data()

        self.assertDictContainsSubset(self.trip_data, trip)

if __name__ == "__main__":
    unittest.main()
