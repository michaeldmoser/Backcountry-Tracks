import unittest

import uuid

from tptesting.fakeriak import RiakClientFake
from tptesting import environment

from bctservices.crud import BasicCRUDService

class TestBasicCRUDServiceCreate(unittest.TestCase):

    def setUp(self):
        environ = environment.create()
        self.owner = 'bob@smith.com'
        self.trip = environ.data['trips'][0]

        riak = RiakClientFake()
        self.bucket = riak.bucket('trips')

        self.gear_result = self.trip.copy()
        self.gear_result.update({'owner': self.owner})

        trip = BasicCRUDService(riak(), 'trips')
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

class TestBasicCRUDServiceUpdate(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()
        self.owner = 'bob@smith.com'
        self.trip = self.environ.data['trips'][0].copy()
        self.trip.update({
                'owner': self.owner,
                'id': str(uuid.uuid4()),
                })

        riak = RiakClientFake()
        self.bucket = riak.bucket('trips')
        self.bucket.add_document(self.trip['id'], self.trip)

        self.trip_result = self.trip.copy()
        self.trip_result['name'] = 'booya'

        tripsdb = BasicCRUDService(riak(), 'trips')
        self.result = tripsdb.update(self.owner, self.trip['id'], self.trip_result)

    def test_update_trip(self):
        '''Updating a piece trip saves to database'''
        document = self.bucket.documents.values()[0]
        self.assertEquals(self.trip_result, document)

    def test_key_id(self):
        '''The riak object key and the trip id should be the same'''
        key = self.bucket.documents.keys()[0]
        id = self.result['id']
        self.assertEquals(key, id)

class TestBasicCRUDServiceDelete(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()
        self.owner = 'bob@smith.com'
        self.trip = self.environ.data['trips'][0].copy()
        self.trip.update({
                'owner': self.owner,
                'id': str(uuid.uuid4()),
                })


        riak = RiakClientFake()
        self.bucket = riak.bucket('trips')
        self.bucket.add_document(self.trip['id'], self.trip)

        tripsdb = BasicCRUDService(riak(), 'trips')
        self.result = tripsdb.delete(self.owner, self.trip['id'])

    def test_delete_trip(self):
        '''Delete a trips saves to database'''
        self.assertEquals(len(self.bucket.documents), 0)

class TestTripsList(unittest.TestCase):

    def test_get_list(self):
        """get list of trips"""
        environ = environment.create()
        trips_data = environ.data['trips']
        
        owner = 'bob@smith.com'
        def add_owner(trip):
            owned_trip = trip.copy()
            owned_trip['owner'] = owner
            return owned_trip
        trips_list = map(add_owner, trips_data)

        riak = RiakClientFake()
        riak.add_mapreduce_result(trips_list, BasicCRUDService.list_mapreduce, 
                {'arg': {'owner': owner}})

        trips = BasicCRUDService(riak(), 'trips')

        actual_list = trips.list(owner)
        self.assertEquals(trips_list, actual_list)

class TestAdventurerRepositoryGet(unittest.TestCase):

    def test_returns_requested_user(self):
        '''Should return requested user'''
        bucket_name = 'adventurer'
        environ = environment.create()
        riakclient = RiakClientFake()
        riakclient()
        adventurer_bucket = riakclient.bucket(bucket_name)
        adventurer_bucket.add_document(environ.ramona.email, environ.ramona)

        adventurer = BasicCRUDService(riakclient, bucket_name)

        user = adventurer.get(environ.ramona.email)
        self.assertEquals(environ.ramona, user)

    def test_no_document_exists(self):
        '''No such document'''
        bucket_name = 'adventurer'
        environ = environment.create()
        riakclient = RiakClientFake()
        riakclient()
        riakclient.bucket(bucket_name) # make sure the bucket is created

        adventurer = BasicCRUDService(riakclient, bucket_name)
        user = adventurer.get(environ.ramona.email)
        self.assertIsNone(user)

    def test_unicode_keys(self):
        '''Should accept unicode keys'''
        bucket_name = 'adventurer'
        environ = environment.create()
        riakclient = RiakClientFake()
        riakclient()
        adventurer_bucket = riakclient.bucket(bucket_name)
        adventurer_bucket.add_document(environ.ramona.email, environ.ramona)

        adventurer = BasicCRUDService(riakclient, bucket_name)

        user = adventurer.get(unicode(environ.ramona.email))
        self.assertEquals(environ.ramona, user)


if __name__ == "__main__":
    unittest.main()


