import unittest
from tptesting import environment

from tptesting.fakepika import SelectConnectionFake
from tptesting.fakeriak import RiakClientFake
from bctmessaging.remoting import RemotingClient

import uuid

from adventurer.users import UserService

class TestUserCreation(unittest.TestCase):
    def setUp(self):
        env = environment.create()
        riak = RiakClientFake()
        bucket_name = 'adventurer'
        bucket = riak.bucket(bucket_name)

        pika_connection = SelectConnectionFake()
        channel = pika_connection._channel
        rpc_client = RemotingClient(channel)

        app = UserService(
                bucket_name = bucket_name, 
                db = riak,
                remoting = rpc_client
                )

        self.app = app
        self.riak = riak
        self.bucket = bucket
        self.env = env
        self.channel = channel

    def test_saves_new_user(self):
        '''Should save user document in database'''
        douglas = self.env.douglas
        douglas.mark_registered()
        douglas['password'] = '1234'
        douglas.for_storage()

        new_user = self.app.save(douglas)
        key = new_user['key']
        userobj = self.bucket.get(key)

        self.assertEquals(new_user, userobj.get_data())

    def test_saves_existing_user(self):
        '''Should save over an existing users data'''
        douglas = self.env.douglas
        douglas.mark_registered()
        douglas['password'] = '1234'
        douglas['key'] = str(uuid.uuid4())
        self.bucket.add_document(douglas['key'], douglas.for_storage())

        douglas['last_name'] = 'Dougy'
        self.app.save(douglas)

        doug_in_db = self.bucket.get(douglas['key']) 
        doug_data = doug_in_db.get_data()

        self.assertEquals(doug_data, douglas)

    def test_creates_email_reference(self):
        '''Should create a reference to the user keyed by the email address'''
        douglas = self.env.douglas
        douglas.mark_registered()
        douglas['password'] = '1234'
        douglas['key'] = str(uuid.uuid4())

        self.app.save(douglas)

        email_ref_obj = self.bucket.get(douglas['email'])
        email_ref = email_ref_obj.get_data()
        self.assertEquals(email_ref['key'], douglas['key'])

        
class TestUserRetrieval(unittest.TestCase):
    def setUp(self):
        env = environment.create()
        riak = RiakClientFake()
        bucket_name = 'adventurer'
        bucket = riak.bucket(bucket_name)

        pika_connection = SelectConnectionFake()
        channel = pika_connection._channel
        rpc_client = RemotingClient(channel)

        app = UserService(
                bucket_name = bucket_name, 
                db = riak,
                remoting = rpc_client
                )

        self.app = app
        self.riak = riak
        self.bucket = bucket
        self.env = env
        self.channel = channel

        self.douglas = self.app.save(self.env.douglas.for_storage())

    def test_get_user_by_id(self):
        '''Retrieve the user object by id'''
        user = self.app.get_by_id(self.douglas['key'])
        self.assertEquals(user, self.douglas)

    def test_get_user_by_email(self):
        '''Retrieve the user object by id'''
        user = self.app.get_by_email(self.douglas['email'])
        self.assertEquals(user, self.douglas)
        


if __name__ == '__main__':
    unittest.main()

