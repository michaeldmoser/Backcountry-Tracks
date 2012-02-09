import unittest

import json
import types

from tptesting import environment

from tptesting.fakepika import SelectConnectionFake
from bctmessaging.remoting import RemotingClient

from adventurer.service import AdventurerRepository
from tptesting.fakeriak import RiakClientFake
from uuid import uuid4

class FakeMailer:
    def send(self, *args):
        pass

class PasswordResetFixture(unittest.TestCase):
    def setUp(self):
        env = environment.create()
        riak = RiakClientFake()
        bucket_name = 'adventurer'
        bucket = riak.bucket(bucket_name)
        fakemail = FakeMailer()

        pika_connection = SelectConnectionFake()
        channel = pika_connection._channel
        rpc_client = RemotingClient(channel)

        douglas = env.douglas
        douglas.mark_registered()
        douglas['password'] = '1234';
        bucket.add_document(douglas.email, douglas)

        app = AdventurerRepository(
                bucket_name = bucket_name, 
                mailer = fakemail, 
                db = riak,
                remoting = rpc_client
                )

        self.app = app
        self.riak = riak
        self.bucket = bucket
        self.env = env
        self.channel = channel

        if hasattr(self, 'continueSetUp'):
            self.continueSetUp()

class TestPasswordReset(PasswordResetFixture):
    def continueSetUp(self):
        douglas = self.env.douglas
        douglas.mark_registered()
        douglas['password'] = '1234';
        self.bucket.add_document(douglas.email, douglas)

        self.app.reset_password(douglas.email)

        douglas_obj = self.bucket.get(douglas.email)

        self.data = douglas_obj.get_data()

    def test_reset_password(self):
        '''User given a password reset code'''
        self.assertIn('password_reset_key', self.data)

    def test_password_is_unchanged(self):
        '''Password should remain unchanged when creating a password reset code'''
        self.assertEquals(self.data['password'], '1234')

class TestRestNonExistingUser(PasswordResetFixture):

    def test_user_doesnt_exist(self):
        '''Should raise an exception if the user doesn't exist'''
        with self.assertRaises(Exception) as err:
            self.app.reset_password('test@example.com')

        self.assertIn("email does not exist", str(err.exception))

class TestPasswordResetEmail(PasswordResetFixture):

    def test_user_should_receive_email(self):
        '''User requesting reset should recieve set email'''
        douglas = self.env.douglas
        douglas.mark_registered()
        douglas['password'] = '1234';
        self.bucket.add_document(douglas.email, douglas)

        self.app.reset_password(douglas.email)

        message = self.channel.messages[0]
        jsonrpc = json.loads(message.body)

        self.assertIn(douglas.email, jsonrpc['params']['to'])

if __name__ == '__main__':
    unittest.main()

