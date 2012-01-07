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
                self.bucket_name
                )

        ramona = self.environ.ramona

        self.trip_id = unicode(uuid4())
        def add_id(gear):
            item = gear.copy()
            item['id'] = str(uuid4())
            return item
        self.gear = map(add_id, self.environ.data['gear'])

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
            'gear': {
                ramona.email: self.gear 
                }
            }
        self.bucket.add_document(self.trip_id, self.trip)

    def test_retrieve_personal_trip_gear(self):
        '''Should return the user's list of gear for the the trip'''
        gear = self.app.get_personal_gear(self.trip_id, self.environ.ramona.email)

        self.assertEquals(gear, self.gear)

    def test_has_no_gear(self):
        '''Retrieve gear for a person that has none'''
        gear = self.app.get_personal_gear(self.trip_id, self.environ.douglas.email)
        self.assertEquals(gear, [])

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
                self.bucket_name
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

class TestTripGearAddPersonalGear(unittest.TestCase):
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
                self.bucket_name
                )

        ramona = self.environ.ramona
        self.ramona = ramona

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

    def create_new_gear(self):
        gear = self.environ.data['gear'][1].copy()
        gear['id'] = str(uuid4())

        return gear

    def get_trip_gear(self):
        stored_trip = self.bucket.get(str(self.trip_id))
        stored_gear = stored_trip.get_data()['gear']

        return stored_gear

    def test_add_personal_gear_item(self):
        '''Add first personal gear'''
        self.bucket.add_document(self.trip_id, self.trip)

        gear = self.create_new_gear()
        self.app.add_personal_gear(self.trip_id, self.ramona.email, gear)

        stored_gear = self.get_trip_gear()

        self.assertEquals(gear, stored_gear[self.ramona.email][0])

    def test_add_person_first_gear(self):
        '''Add a person's first personal gear item to a trip'''
        self.trip['gear'] = {
                self.environ.douglas.email: self.environ.data['gear']
                }
        expected_gear = deepcopy(self.trip['gear'])

        self.bucket.add_document(self.trip_id, self.trip)

        gear = self.create_new_gear()
        expected_gear[self.ramona.email] = [gear]
        self.app.add_personal_gear(self.trip_id, self.ramona.email, gear)

        stored_gear = self.get_trip_gear()

        self.assertEquals(expected_gear, stored_gear)
    
    def test_add_person_additional_gear(self):
        '''Add a person's second personal gear item to a trip'''
        trip_gear = {
                self.environ.douglas.email: self.environ.data['gear'],
                self.ramona.email: [self.environ.data['gear'][0].copy()]
                }
        self.trip['gear'] = trip_gear
        self.bucket.add_document(self.trip_id, self.trip)

        gear = self.create_new_gear()
        trip_gear[self.ramona.email].append(gear)
        self.app.add_personal_gear(self.trip_id, self.ramona.email, gear)

        stored_gear = self.get_trip_gear()

        self.assertEquals(stored_gear, trip_gear)
    
if __name__ == '__main__':
    unittest.main()

