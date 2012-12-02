import unittest
import uuid
import copy

from tptesting import environment
from tptesting.testcases import RiakFakeTestCase

from trips.tripscoreservice import TripsCoreService

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
        self.service.create(self.adventurer, self.trip)

    def test_store_item_to_inventory(self):
        '''Adding to inventory saves gear document to database'''
        riak_doc = self.bucket.documents[self.piece_of_gear.key]
        self.assertDictContainsSubset(self.piece_of_gear, riak_doc)

    def test_object_type_set_to_gear(self):
        '''object_type of usermeta should be gear'''
        riak_doc = self.bucket.documents[self.piece_of_gear.key]
        self.assertEquals(riak_doc.metadata['usermeta']['object_type'], self.BUCKET)

    def test_gear_added_to_index(self):
        '''The gear should be added to the adventurers gear index'''
        riak_doc = self.bucket.documents[self.adventurer]
        self.assertIn(self.piece_of_gear.key, riak_doc['documents'])

