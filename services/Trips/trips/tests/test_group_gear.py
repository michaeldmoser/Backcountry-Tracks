import unittest

from copy import deepcopy

from uuid import uuid4
import json

from tptesting import environment

from trips.service import TripsDb
from tptesting.fakeriak import RiakClientFake
from tptesting.fakepika import SelectConnectionFake
from bctmessaging.remoting import RemotingClient

from trips.tests import utils

class TestTripGearRetrieval(utils.TestTripFixture):

    def continueSetUp(self):
        trip = self.bucket.get(str(self.trip_id))
        def add_data(gear):
            item = gear.copy()
            item['id'] = str(uuid4())
            item['owner'] = self.environ.ramona.email
            return item
        self.gear = map(add_data, self.environ.data['gear'])

        for piece_of_gear in self.gear:
            obj = self.bucket.new(piece_of_gear['id'], piece_of_gear)
            obj.set_usermeta({'object_type': 'gear_group'})
            obj.store()

            trip.add_link(obj, tag="gear_group")

        trip.store()

    def test_retrieve_trip_group_gear(self):
        '''Should return the shared gear for a trip'''
        gear = self.app.get_group_gear(self.trip_id)
        actual_keys = [item['id'] for item in gear]
        actual_keys.sort()

        expected_keys = [item['id'] for item in self.gear]
        expected_keys.sort()

        self.assertEquals(expected_keys, actual_keys)

class TestTripGearRetrievalNone(utils.TestTripFixture):

    def test_groupgear_is_empty(self):
        '''Should return empty list if there is not group gear'''
        gear = self.app.get_group_gear(self.trip_id)

        self.assertEquals(gear, [])

class TestTripGearShare(utils.TestTripFixture):

    def test_share_gear(self):
        '''Share a piece of gear with trip should create new document for gear'''
        gear_to_share = self.environ.data['gear'][0].copy()
        gear_to_share['id'] = str(uuid4())
        gear_to_share['owner'] = self.environ.douglas.email

        self.app.share_gear(self.trip_id, gear_to_share)

        gearobj = self.bucket.get(str(gear_to_share['id']))

        self.assertTrue(gearobj.exists())
        
    def test_share_more_gear(self):
        '''Share a second piece of gear with trip'''
        def share_gear(item):
            gear_to_share = item.copy()
            gear_to_share['id'] = str(uuid4())
            gear_to_share['owner'] = self.environ.douglas.email

            self.app.share_gear(self.trip_id, gear_to_share)
            return gear_to_share
        expected_gear = map(share_gear, self.environ.data['gear'])
        expected_ids = [gear['id'] for gear in expected_gear]
        expected_ids.sort()

        tripobj = self.bucket.get(str(self.trip_id))
        links = tripobj.get_links()
        actual_ids = [link.get_key() for link in links]
        actual_ids.sort()

        self.assertEquals(actual_ids, expected_ids)

class TestTripGearUnshare(utils.TestTripFixture):

    def continueSetUp(self):
        def share_gear(item):
            gear_to_share = item.copy()
            gear_to_share['id'] = str(uuid4())
            gear_to_share['owner'] = self.environ.douglas.email

            self.app.share_gear(self.trip_id, gear_to_share)
            return gear_to_share
        self.gear = map(share_gear, self.environ.data['gear'])

    def test_unshare_gear(self):
        '''Unshare gear should remove from group gear list'''
        gear = self.app.unshare_gear(self.trip_id, self.gear[0]['id'])

        tripobj = self.bucket.get(str(self.trip_id))
        links = tripobj.get_links()
        gear_ids = [link.get_key() for link in links]

        self.assertNotIn(self.gear[0]['id'], gear_ids)

    def test_unshare_gear_is_removed(self):
        '''Unshare gear should remove from group gear list'''
        gear = self.app.unshare_gear(self.trip_id, self.gear[0]['id'])

        gearobj = self.bucket.get(str(self.gear[0]['id']))
        self.assertFalse(gearobj.exists())

class TestSharePersonalGear(utils.TestTripFixture):
    def continueSetUp(self):
        def share_gear(item):
            gear_to_share = item.copy()
            gear_to_share['id'] = str(uuid4())
            gear_to_share['owner'] = self.environ.douglas.email

            self.app.add_personal_gear(self.trip_id, gear_to_share['owner'], gear_to_share)
            return gear_to_share
        self.gear = map(share_gear, self.environ.data['gear'])

    def test_personal_gear_link_removed(self):
        '''When sharing gear from the personal gear with the group remove the link to the personal gear'''
        self.app.share_gear(self.trip_id, self.gear[0])

        personal_gear = self.app.get_personal_gear(self.trip_id, self.environ.douglas.email)
        personal_gear_ids = map(lambda x: x['id'], personal_gear)
        self.assertNotIn(self.gear[0]['id'], personal_gear_ids)

if __name__ == '__main__':
    unittest.main()

