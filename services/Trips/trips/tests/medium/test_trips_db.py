import pdb
import unittest
import urllib2

from uuid import uuid4
import json

from tptesting import environment

class TestTripsServiceCreate(unittest.TestCase):

    def get_sut_trip(self):
        trip_list_request = urllib2.Request(self.trip_url)
        response = self.login_session.open(trip_list_request)
        trips = json.loads(response.read())

        return trips[0]

    def create_request(self, url, data = None, method = 'GET'):
        json_data = None if data is None else json.dumps(data)
        trip_request = urllib2.Request(
                self.trip_url + url,
                data = json_data
                )
        trip_request.get_method = lambda: method

        return trip_request

    def do_request(self, url, data = None, method = 'GET'):
        request = self.create_request(url, data = data, method = method)
        self.response = self.login_session.open(request)
        body = self.response.read()
        if len(body) < 1:
            return None

        data = json.loads(body)

        return data

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

        cls.login_session = albert.login()

    def setUp(self):
        self.environ.trips.remove_all()
        self.created_trip = self.do_request('', data = self.trip, method = 'POST')

    def test_created_gear_can_be_retrieved(self):
        '''Created gear can be retrieved via list operation'''
        trip = self.get_sut_trip()
        self.assertEquals(self.created_trip, trip)

    def test_update_trip(self):
        '''Retrieve then update a trip'''
        trip = self.get_sut_trip()
        trip['name'] = 'Test Trip 2'
        trip_id = trip['id']
        
        url = "/%s" % trip_id
        updated_trip_response = self.do_request(url, data = trip, method = 'PUT')

        stored_trip = self.get_sut_trip()

        self.assertEquals(updated_trip_response, stored_trip)

    def test_delete_trip(self):
        '''Delete a trip from the database'''
        trip_id = self.created_trip['id']
        url = "/%s" % trip_id
        self.do_request(url, method = 'DELETE')

        trips = self.do_request('')

        self.assertEquals(len(trips), 0)

if __name__ == '__main__':
    unittest.main()


