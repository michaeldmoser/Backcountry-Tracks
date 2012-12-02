import pdb
import unittest
import urllib2

from uuid import uuid4
import json

from tptesting import environment

class TestTripsServiceCreate(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()

        trips = cls.environ.trips
        albert = cls.environ.albert
        cls.user = cls.environ.create_user(albert)


        cls.trip = {
                'route_description': '',
                'trip_distance': '',
                'elevation_gain': '',
                'difficulty': '',
                'name': 'Test 1',
                'description': 'Test trip 1',
                'start': '2012-12-01',
                'end': '2012-12-05'
                }

        cls.trip_url = cls.environ.trailhead_url + '/trips'
        trip_request = urllib2.Request(
                cls.trip_url,
                data = json.dumps(cls.trip)
                )
        #trip_request.get_method = lambda: 'PUT'

        cls.login_session = albert.login()
        cls.response = cls.login_session.open(trip_request)
        body = cls.response.read()
        cls.created_trip = json.loads(body)

        cls.bucket = cls.environ.riak.get_database('trips')

    def test_create_a_piece_of_gear(self):
        '''Created gear can be retrieved via list operation'''
        trip_list_request = urllib2.Request(self.trip_url)
        response = self.login_session.open(trip_list_request)
        trips = json.loads(response.read())

        self.assertEquals(self.created_trip, trips[0])




if __name__ == '__main__':
    unittest.main()


