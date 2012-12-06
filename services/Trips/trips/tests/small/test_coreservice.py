import unittest
import uuid
import copy

from tptesting import environment
from tptesting.testcases import RiakFakeTestCase

from trips.coreservice import TripsCoreService

class TestTripCreate(RiakFakeTestCase):
    BUCKET = 'trips'

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

class TestTripDelete(RiakFakeTestCase):
    BUCKET = 'trips'

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

    def test_delete_removes_from_db(self):
         '''Deleting removes trip from database'''
         self.service.delete(self.adventurer, self.stored_trip['id'])

         documents = self.bucket.documents
         trip_id = self.stored_trip['id']
         self.assertFalse(documents.has_key(trip_id))

    def test_delete_remotes_from_index(self):
        '''Should remove the trip from the owner's index document'''
        trip_id = self.stored_trip['id']
        self.service.delete(self.adventurer, trip_id)

        index_doc = self.bucket.documents[self.adventurer]
        self.assertNotIn(trip_id, index_doc['documents'])

    def test_delete_non_existant_trip(self):
        '''Delete a trip that doesn't exists should do nothing'''
        self.service.delete(self.adventurer, str(uuid.uuid4()))


if __name__ == '__main__':
    unittest.main()


