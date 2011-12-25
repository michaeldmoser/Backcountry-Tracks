import unittest

from uuid import uuid4
import json

from tptesting import environment

from trips.service import TripsDb
from tptesting.fakeriak import RiakClientFake
from tptesting.fakepika import SelectConnectionFake
from bctmessaging.remoting import RemotingClient

class TestTripsDbInvite(unittest.TestCase):

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

        self.trip_id = unicode(uuid4())
        self.bucket.add_document(self.trip_id, {
            'name': 'Glacier',
            'start': '2012-07-19',
            'end': '2012-07-24',
            'destination': 'Glacier National Park'
            })
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
        self.assertEquals(self.result['id'], self.invite['email'])

    def test_saved_to_database(self):
        '''Invite should be saved in the database'''
        trip_obj = self.bucket.get(str(self.trip_id))
        trip = trip_obj.get_data()

        invite = trip['friends'][0]

        self.assertEquals(self.result, invite)

    def test_saves_multiple_invites(self):
        '''Should save additional invites while retaining old ones'''
        additional_invite = {
                'email': self.environ.albert.email,
                'first': self.environ.albert.first_name,
                'last': self.environ.albert.last_name,
                'invite_status': 'invited'
                }
        invite_result = self.app.invite(self.trip_id, self.environ.ramona.email,
                additional_invite)

        trip_obj = self.bucket.get(str(self.trip_id))
        trip = trip_obj.get_data()

        invites = trip['friends']

        expected_invites = [self.result, invite_result]
        self.assertEquals(invites, expected_invites)

class TestSendsInviteEmail(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()
        self.riak = RiakClientFake()
        self.bucket_name = 'trips'
        self.bucket = self.riak.bucket(self.bucket_name)

        pika_connection = SelectConnectionFake()
        self.channel = pika_connection._channel
        rpc_client = RemotingClient(self.channel)

        self.app = TripsDb(
                rpc_client,
                self.riak,
                self.bucket_name
                )

        self.trip_id = unicode(uuid4())
        self.bucket.add_document(self.trip_id, {
            'name': 'Glacier',
            'start': '2012-07-19',
            'end': '2012-07-24',
            'destination': 'Glacier National Park'
            })
        self.invite = {
                'email': self.environ.douglas.email,
                'first': self.environ.douglas.first_name,
                'last': self.environ.douglas.last_name,
                'invite_status': 'invited'
                }
        self.result = self.app.invite(self.trip_id, self.environ.ramona.email, self.invite)

        self.message = self.channel.messages[0]
        self.jsonrpc = json.loads(self.message.body)

    def test_sends_invite(self):
        '''A message should be sent'''
        expected = {
                'jsonrpc': '2.0',
                'method': 'send'
                }

        self.assertDictContainsSubset(expected, self.jsonrpc)

    def test_message_sent_to_person(self):
        '''The message should be sent to Douglas'''
        to = self.jsonrpc['params']['to']
        self.assertEquals(self.environ.douglas.email, to)

    def test_message_subject(self):
        '''The subject should set'''
        subject = self.jsonrpc['params'].get('subject', None)
        self.assertIsNotNone(subject)

    def test_message_body(self):
        '''The message should not be empty'''
        body = self.jsonrpc['params'].get('message')
        self.assertIsNotNone(body)

class TestAccept(unittest.TestCase):
    def setUp(self):
        self.environ = environment.create()
        self.riak = RiakClientFake()
        self.bucket_name = 'trips'
        self.bucket = self.riak.bucket(self.bucket_name)

        pika_connection = SelectConnectionFake()
        self.channel = pika_connection._channel
        rpc_client = RemotingClient(self.channel)

        self.app = TripsDb(
                rpc_client,
                self.riak,
                self.bucket_name
                )

        self.trip_id = str(uuid4())
        self.invite = {
                'email': self.environ.douglas.email,
                'first': self.environ.douglas.first_name,
                'last': self.environ.douglas.last_name,
                'invite_status': 'invited'
                }
        self.bucket.add_document(self.trip_id, {
            'name': 'Glacier',
            'start': '2012-07-19',
            'end': '2012-07-24',
            'destination': 'Glacier National Park',
            'friends': [self.invite]
            })
        self.result = self.app.accept(self.trip_id, self.environ.douglas.email)

    def test_invite_changed_to_accepted(self):
        '''Accept should update the invite status to accepted'''
        trip = self.bucket.get(self.trip_id).get_data()
        invite_status = trip['friends'][0]['invite_status']
        self.assertEquals(invite_status, 'accepted')

    def test_invite_returns(self):
        '''Accept should return the updated invite'''
        invite = self.invite.copy()
        invite['invite_status'] = 'accepted'
        self.assertEquals(invite, self.result)


if __name__ == '__main__':
    unittest.main()


