import unittest

import riak

from tptesting import environment, fakepika
from bctmessaging.remoting import RemotingClient

from trips.service import TripsDb

class TestTripListing(unittest.TestCase):

    def test_list_of_trips_for_invitee(self):
        '''TripsDb.list() should return trips a user is invited on'''
        env = environment.create()
        env.make_pristine()
        env.bringup_infrastructure()

        env.create_user(env.douglas)
        env.create_user(env.ramona)
        trips = env.trips.add_trips_to_user(env.douglas, env.data['trips'])

        env.trips.add_invitee(trips[0]['id'], env.ramona, 'invited')

        client = riak.RiakClient()
        pika = fakepika.SelectConnectionFake()
        remoting = RemotingClient(pika._channel)

        tripsdb = TripsDb(remoting, client, 'trips', 'http://test.com')

        invited_on = tripsdb.list(env.ramona.email)
        invited_on[0]['friends'] = []

        self.assertDictContainsSubset(env.data['trips'][0], invited_on[0])


class TestTripListingWithIgnored(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.env = environment.create()
        cls.env.make_pristine()
        cls.env.bringup_infrastructure()

        cls.env.create_user(cls.env.douglas)
        cls.env.create_user(cls.env.ramona)
        trips = cls.env.trips.add_trips_to_user(cls.env.douglas, cls.env.data['trips'])

        cls.env.trips.add_invitee(trips[0]['id'], cls.env.ramona, 'invited')
        cls.env.trips.add_invitee(trips[1]['id'], cls.env.ramona, 'not coming')

        client = riak.RiakClient()
        pika = fakepika.SelectConnectionFake()
        remoting = RemotingClient(pika._channel)

        tripsdb = TripsDb(remoting, client, 'trips', 'http://test.com')

        cls.invited_on = tripsdb.list(cls.env.ramona.email)
        cls.invited_on[0]['friends'] = []

    def test_accepted_trip(self):
        '''TripsDb.list() should return trips a user is invited on but has not ignored'''
        self.assertDictContainsSubset(self.env.data['trips'][0], self.invited_on[0])

    def test_list_does_not_contain_ignored(self):
        '''TripsDb.list() should return only one trip'''
        self.assertEquals(len(self.invited_on), 1)


if __name__ == '__main__':
    unittest.main()


