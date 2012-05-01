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

class TestTripGearRetrievalNoGear(unittest.TestCase):

    def test_no_gear_section(self):
        '''There is no gear section'''
        self.environ = environment.create()
        self.riak = RiakClientFake()
        self.bucket_name = 'trips'
        self.bucket = self.riak.bucket(self.bucket_name)

        pika_connection = SelectConnectionFake()
        channel = pika_connection._channel
        rpc_client = RemotingClient(channel)

        self.app = TripsDb(
                rpc_client,
                self.riak,
                self.bucket_name,
                'http://test.com'
                )

        ramona = self.environ.ramona

        self.trip_id = unicode(uuid4())
        self.trip = {
            'name': 'Glacier',
            'start': '2012-07-19',
            'end': '2012-07-24',
            'destination': 'Glacier National Park',
            'friends': [
                {'first': ramona.first_name,
                    'last': ramona.last_name,
                    'email': ramona.email,
                    'invite_status': 'accepted'}
                ],
            }
        self.bucket.add_document(self.trip_id, self.trip)

        gear = self.app.get_personal_gear(self.trip_id, self.environ.ramona.email)
        self.assertEquals(gear, [])

class TestTripGearRemove(utils.TestTripFixture):

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
            obj.set_usermeta({'object_type': 'gear_personal'})
            obj.store()

            trip.add_link(obj, tag="gear_personal")

        trip.store()

        gear = self.gear[0]
        self.app.remove_personal_gear(self.trip_id, self.environ.ramona.email, gear['id'])

    def test_remove_personal_trip_gear(self):
        '''Gear item should not be present in the trips database'''
        gearobj = self.bucket.get(str(self.gear[0]['id']))
        self.assertFalse(gearobj.exists())

    def test_remove_personal_trip_gear_link(self):
        '''Gear item should not be linked in the trip'''
        tripobj = self.bucket.get(str(self.trip_id))
        links = tripobj.get_links()
        gear_ids = [link.get_key() for link in links]
        self.assertNotIn(self.gear[0]['id'], gear_ids)

class TestRetrieveLinkedPersonalGear(utils.TestTripFixture):
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
            obj.set_usermeta({'object_type': 'gear_personal'})
            obj.store()

            trip.add_link(obj, tag="gear_personal")

        trip.store()

    def test_get_personal_gear(self):
        '''Should return personal gear from trips database'''
        personal_gear = self.app.get_personal_gear(self.trip_id, self.environ.ramona.email)
        stored_gear_ids = [gear['id'] for gear in personal_gear]
        expected_gear_ids = [gear['id'] for gear in self.gear]
        stored_gear_ids.sort()
        expected_gear_ids.sort()

        self.assertEquals(expected_gear_ids, stored_gear_ids)

class TestRetrieveLinkedPersonalGearNone(utils.TestTripFixture):
    def test_get_personal_gear_no_gear(self):
        '''Should return an empty list of gear if no gear present on the trip'''
        personal_gear = self.app.get_personal_gear(self.trip_id, self.environ.ramona.email)

        self.assertEquals(personal_gear, [])

    def test_get_personal_gear_user(self):
        '''There is personal gear on the trip but not for this user'''
        trip = self.bucket.get(str(self.trip_id))
        def add_data(gear):
            item = gear.copy()
            item['id'] = str(uuid4())
            item['owner'] = self.environ.ramona.email
            return item
        self.gear = map(add_data, self.environ.data['gear'])

        for piece_of_gear in self.gear:
            obj = self.bucket.new(piece_of_gear['id'], piece_of_gear)
            obj.set_usermeta({'object_type': 'gear_personal'})
            obj.store()

            trip.add_link(obj, tag="gear_personal")

        trip.store()
        personal_gear = self.app.get_personal_gear(self.trip_id, self.environ.douglas.email)

        self.assertEquals(personal_gear, [])

class TestAddLinkedPersonalGear(utils.TestTripFixture):

    def test_add_personal_gear_via_links(self):
        '''Add personal gear to a trip'''
        gear = self.environ.data['gear'][0]
        gear['id'] = str(uuid4())
        gear['owner'] = self.environ.ramona.email
        
        self.app.add_personal_gear(self.trip_id, self.environ.ramona.email, gear)

        trip = self.bucket.get(str(self.trip_id))
        links = trip.get_links()
        gear_links = filter(lambda x: x.get_tag() == 'gear_personal', links)

        self.assertEquals(gear['id'], gear_links[0].get_key())

    def test_add_multi_personal_gear_via_links(self):
        def build_gear(item):
            gear = item.copy()
            gear['id'] = str(uuid4())
            gear['owner'] = self.environ.ramona.email
            self.app.add_personal_gear(self.trip_id, self.environ.ramona.email, gear)
            return gear
        personal_gear = map(build_gear, self.environ.data['gear'])

        trip = self.bucket.get(str(self.trip_id))
        links = trip.get_links()
        gear_links = filter(lambda x: x.get_tag() == 'gear_personal', links)
        actual_gear_ids = map(lambda x: x.get_key(), gear_links)
        actual_gear_ids.sort()

        expected_gear_ids = map(lambda x: x['id'], personal_gear)
        expected_gear_ids.sort()

        self.assertEquals(expected_gear_ids, actual_gear_ids)

class TestPutGroupGearBack(utils.TestTripFixture):
    def continueSetUp(self):
        def share_gear(item):
            gear_to_share = item.copy()
            gear_to_share['id'] = str(uuid4())
            gear_to_share['owner'] = self.environ.douglas.email

            self.app.share_gear(self.trip_id, gear_to_share)
            return gear_to_share
        self.gear = map(share_gear, self.environ.data['gear'])

    def test_personal_gear_link_removed(self):
        '''When sharing gear from the personal gear with the group remove the link to the personal gear'''
        self.app.add_personal_gear(self.trip_id, self.gear[0]['owner'], self.gear[0])

        group_gear = self.app.get_group_gear(self.trip_id)
        group_gear_ids = map(lambda x: x['id'], group_gear)
        self.assertNotIn(self.gear[0]['id'], group_gear_ids)

    
if __name__ == '__main__':
    unittest.main()

