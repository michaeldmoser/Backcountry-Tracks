import unittest

from tptesting import environment

from trips.service import TripsDb
from tptesting.fakeriak import RiakClientFake
from uuid import uuid4

class TestTripsDbInvite(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()
        self.riak = RiakClientFake()
        self.bucket_name = 'trips'
        self.bucket = self.riak.bucket(self.bucket_name)

        self.app = TripsDb(
                self.riak,
                self.bucket_name
                )

        self.trip_id = unicode(uuid4())
        self.bucket.add_document(self.trip_id, {})
        self.invite = {
                'email': self.environ.douglas.email,
                'first': self.environ.douglas.first_name,
                'last': self.environ.douglas.last_name,
                'invite_status': 'invited'
                }
        self.result = self.app.invite(self.trip_id, self.environ.ramona.email, self.invite)

    def test_response(self):
        '''Should respond with invite'''
        self.assertDictContainsSubset(self.invite, self.result)

    def test_id_in_response(self):
        '''There should be an id in the response'''
        self.assertIn('id', self.result)

    def test_saved_to_database(self):
        '''Invite should be saved in the database'''
        trip_obj = self.bucket.get(str(self.trip_id))
        trip = trip_obj.get_data()

        invite = trip['friends'][0]

        self.assertDictContainsSubset(self.result, invite)

if __name__ == '__main__':
    unittest.main()


