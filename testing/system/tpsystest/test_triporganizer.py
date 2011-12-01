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

        cls.trip_data = cls.environ.data['trips'][0] 
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

class EditTrip(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()


        trips = cls.environ.trips
        albert = cls.environ.albert
        cls.environ.create_user(albert)

        login_session = albert.login() 

        cls.old_trip = cls.environ.data['trips'][0].copy()
        cls.old_trip['owner'] = albert.email

        cls.trip_id = trips.add(**cls.old_trip)
        cls.old_trip['id'] = cls.trip_id

        trip_url = cls.environ.trailhead_url + '/trips/' + cls.trip_id

        cls.updated_trip = cls.old_trip.copy()
        cls.updated_trip.update({
                'name': 'Gila Wilderness - March 2011',
                'description': '5 day 40 mile hike through the Gila Wilderness',
                'start': '2011-03-21',
                'end': '2011-03-25'
                })
        trip_update_request = urllib2.Request(
                trip_url,
                data=json.dumps(cls.updated_trip),
                headers={'Content-Type': 'application/json'} 
                )
        trip_update_request.get_method = lambda: 'PUT'

        cls.response = login_session.open(trip_update_request)
        body = cls.response.read()
        cls.response = json.loads(body)

    def test_gear_item_returned(self):
        '''Should receive the gear item back'''
        self.assertEquals(self.updated_trip, self.response)

    def test_gear_in_database(self):
        '''The new piece of gear should be in the personal_gear database'''
        bucket = self.environ.riak.get_database('trips')
        doc_object = bucket.get(self.trip_id)
        trip = doc_object.get_data()

        self.assertDictContainsSubset(self.updated_trip, trip)

class DeleteTrip(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()


        trips = cls.environ.trips
        albert = cls.environ.albert
        cls.environ.create_user(albert)

        login_session = albert.login() 

        cls.trip = cls.environ.data['trips'][0].copy()
        cls.trip['owner'] = albert.email
        cls.trip_id = cls.environ.trips.add(**cls.trip)
        cls.trip['id'] = cls.trip_id

        trip_url = cls.environ.trailhead_url + '/trips/' + cls.trip_id

        trip_delete_request = urllib2.Request(trip_url)
        trip_delete_request.get_method = lambda: 'DELETE'

        cls.response = login_session.open(trip_delete_request)

    def test_gear_item_returned(self):
        '''Should receive 204 no content'''
        self.assertEquals(204, self.response.code)

    def test_gear_in_database(self):
        '''The new piece of gear should be in the trips database'''
        bucket = self.environ.riak.get_database('trips')
        def key_should_not_exist():
            keys = bucket.get_keys()
            self.assertEquals([], keys)
        utils.try_until(100, key_should_not_exist)

class RetrieveTripList(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()


        trips = cls.environ.trips
        albert = cls.environ.albert
        cls.environ.create_user(albert)

        cls.trips_data = cls.environ.trips.add_trips_to_user(albert,
                cls.environ.data['trips'])

        login_session = albert.login() 

        trips_list_url = cls.environ.trailhead_url + '/trips'
        trips_list_request = urllib2.Request(
                trips_list_url
                )

        cls.response = login_session.open(trips_list_request)
        body = cls.response.read()
        cls.trips_list = json.loads(body)

    def test_list_of_trips_has_0(self):
        """Test /app/trips returns a list of trips"""
        self.assertIn(self.trips_data[0], self.trips_list)

    def test_list_of_trips_has_2(self):
        """Test /app/trips returns a list of trips"""
        self.assertIn(self.trips_data[2], self.trips_list)

if __name__ == "__main__":
    unittest.main()
