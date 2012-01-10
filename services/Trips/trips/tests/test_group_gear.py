import unittest

from copy import deepcopy

from uuid import uuid4
import json

from tptesting import environment

from trips.service import TripsDb
from tptesting.fakeriak import RiakClientFake
from tptesting.fakepika import SelectConnectionFake
from bctmessaging.remoting import RemotingClient

class TestTripGearRetrieval(unittest.TestCase):

    def setUp(self):
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


        self.trip_id = unicode(uuid4())
        def add_id(gear):
            item = gear.copy()
            item['id'] = str(uuid4())
            return item
        self.gear = map(add_id, self.environ.data['gear'])

        ramona = self.environ.ramona
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
            'gear': dict(),
            'groupgear': list()
            }

    def test_retrieve_trip_group_gear(self):
        '''Should return the shared gear for a trip'''
        self.trip['groupgear'] = self.gear
        self.bucket.add_document(self.trip_id, self.trip)
        gear = self.app.get_group_gear(self.trip_id)

        self.assertEquals(gear, self.gear)

    def test_groupgear_is_empty(self):
        '''Should return empty list if there is not group gear'''
        self.bucket.add_document(self.trip_id, self.trip)
        gear = self.app.get_group_gear(self.trip_id)

        self.assertEquals(gear, [])

    def test_groupgear_is_empty(self):
        '''Should return empty list if there is not group gear'''
        del self.trip['groupgear']
        self.bucket.add_document(self.trip_id, self.trip)
        gear = self.app.get_group_gear(self.trip_id)

        self.assertEquals(gear, [])

    def test_share_gear(self):
        '''Share a piece of gear with trip'''
        del self.trip['groupgear']
        self.bucket.add_document(self.trip_id, self.trip)

        gear = self.app.share_gear(self.trip_id, self.gear[0])

        tripobj = self.bucket.get(str(self.trip_id))
        trip = tripobj.get_data()
        groupgear = trip.get('groupgear', [])

        self.assertIn(self.gear[0], groupgear)
        
    def test_share_more_gear(self):
        '''Share a second piece of gear with trip'''
        self.trip['groupgear'].append(self.gear[0])
        self.bucket.add_document(self.trip_id, self.trip)

        gear = self.app.share_gear(self.trip_id, self.gear[1])

        tripobj = self.bucket.get(str(self.trip_id))
        trip = tripobj.get_data()
        groupgear = trip.get('groupgear', [])

        self.assertEquals(self.gear[0:2], groupgear)


if __name__ == '__main__':
    unittest.main()

