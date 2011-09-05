import unittest

import uuid

from tptesting.fakeriak import RiakClientFake
from tptesting import environment

from trips.db import TripsDb

class TestTripsDbCreate(unittest.TestCase):

    def setUp(self):
        environ = environment.create()
        self.owner = 'bob@smith.com'
        self.trip = environ.data['trips'][0]

        riak = RiakClientFake()
        self.bucket = riak.bucket('trips')

        self.gear_result = self.trip.copy()
        self.gear_result.update({'owner': self.owner})

        trip = TripsDb(riak(), 'trips')
        self.result = trip.create(self.owner, self.trip)

    def test_create_trip(self):
        '''Creating a new trip saves to database'''
        document = self.bucket.documents.values()[0]
        self.assertDictContainsSubset(self.trip, document)

    def test_should_have_id(self):
        '''The return should have an ID key'''
        self.assertIn('id', self.result)

    def test_should_have_owner(self):
        '''Updated trip object returned'''
        self.assertDictContainsSubset(self.gear_result, self.result)

    def test_key_id(self):
        '''The riak object key and the trip id shoudl be the same'''
        key = self.bucket.documents.keys()[0]
        id = self.result['id']
        self.assertEquals(key, id)

if __name__ == "__main__":
    unittest.main()

