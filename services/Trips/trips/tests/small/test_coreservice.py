import unittest
import uuid
import copy

from tptesting import environment
from tptesting.testcases import RiakFakeTestCase

from trips.coreservice import TripsCoreService

class TestTripCreate(RiakFakeTestCase):
    BUCKET = 'gear'

    def continueSetup(self):
        self.trip = {
                'route_description': '',
                'trip_distance': '',
                'elevation_gain': '',
                'difficulty': '',
                'name': 'Test 1',
                'description': 'Test trip 1',
                'start': '2012-12-01',
                'end': '2012-12-05'
                }
        self.service = TripsCoreService(self.riak, self.BUCKET)
        self.stored_trip = self.service.create(self.adventurer, self.trip)

    def test_trip_saved_to_db(self):
        '''Trip gets saved to the database'''
        riak_doc = self.bucket.documents[self.stored_trip['id']]
        self.assertDictContainsSubset(self.trip, riak_doc)

    def test_trip_saved_in_index_doc(self):
        '''The trip is saved in the adventurer's index document'''
        riak_doc = self.bucket.documents[self.adventurer]
        self.assertIn(self.stored_trip['id'], riak_doc['documents'])

    def test_trip_owner_set(self):
        '''The trip should have the owner set'''
        riak_doc = self.bucket.documents[self.stored_trip['id']]
        self.assertEquals(riak_doc['owner'], self.adventurer)


if __name__ == '__main__':
    unittest.main()

