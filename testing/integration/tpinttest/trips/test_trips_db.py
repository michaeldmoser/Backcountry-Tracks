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

        tripsdb = TripsDb(remoting, client, 'trips')

        invited_on = tripsdb.list(env.ramona.email)

        self.assertDictContainsSubset(env.data['trips'][0], invited_on[0])


if __name__ == '__main__':
    unittest.main()


