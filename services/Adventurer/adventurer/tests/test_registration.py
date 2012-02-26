import unittest
import types

from tptesting import environment

from adventurer.service import AdventurerRepository
from tptesting.fakeriak import RiakClientFake
from uuid import uuid4

class TestAdventurerRepository(unittest.TestCase):
    def setUp(self):
        self.environ = environment.create()
        self.riak = RiakClientFake()
        self.bucket_name = 'adventurer'
        self.bucket = self.riak.bucket(self.bucket_name)
        self.fakemail = FakeMailer()

        self.app = AdventurerRepository(
                bucket_name = self.bucket_name, 
                mailer = self.fakemail, 
                db = self.riak
                )

    def test_registration_is_saved(self):
        """The registration is saved to Riak"""
        def confirmation_key_generator():
            return 'generated_confirmation_key'
        self.app.generate_confirmation_key = confirmation_key_generator

        user = self.environ.albert.registration_data()
        self.app.register(**user)
        expected_data = self.environ.albert.for_storage()
        expected_data['confirmation_key'] = 'generated_confirmation_key'

        riak_object = self.bucket.get(self.environ.albert['email'])
        actual_data = riak_object.get_data()

        self.assertEquals(actual_data, expected_data)

    def test_registration_casts_unicode_email_to_string(self):
        """Registration allows Unicode emails"""
        user = self.environ.albert.registration_data()
        user['email'] = unicode('email@test.com')
        self.app.register(**user)

        riak_object = self.bucket.get('email@test.com')
        registered_user = riak_object.get_data()

        self.assertIsNotNone(registered_user)

    def test_registration_sends_confirmation_email(self):
        """Registration sends confirmation email"""
        mailerspy = MailerSpy()
        app = AdventurerRepository(
                bucket_name = self.bucket_name,
                mailer = mailerspy,
                db = self.riak
                )
        user = self.environ.albert.registration_data()
        app.register(**user)

        self.assertTrue(mailerspy.to, user['email'])

    def test_confirmation_email_contains_link_with_confirmation_key(self):
        """Registration email contains confirmation key"""
        trailhead_url = self.environ.get_config_for('trailhead_url');

        mailerspy = MailerSpy()
        app = AdventurerRepository(
                bucket_name = self.bucket_name,
                mailer = mailerspy,
                db = self.riak,
                trailhead_url = trailhead_url
                )

        def confirmation_key_generator():
            return 'generated_confirmation_key'
        app.generate_confirmation_key = confirmation_key_generator
        user = self.environ.albert.copy()
        user['password_again'] = user['password']
        app.register(**user)

        expected_link = '%s/activate/%s/%s' % (
                trailhead_url,
                user['email'],
                'generated_confirmation_key'
                )

        self.assertIn(expected_link, mailerspy.body)

class TestActivation(unittest.TestCase):
    def setUp(self):
        self.environ = environment.create()
        self.riak = RiakClientFake()
        self.bucket_name = 'adventurer'
        self.bucket = self.riak.bucket(self.bucket_name)
        self.fakemail = FakeMailer()

        self.confirmation_key = '1234'
        self.douglas = self.environ.douglas
        self.douglas['confirmation_key'] = self.confirmation_key
        self.bucket.add_document(self.douglas.email, self.douglas)

        self.app = AdventurerRepository(
                bucket_name = self.bucket_name, 
                mailer = self.fakemail, 
                db = self.riak
                )

    def test_successful_registration(self):
        '''Returns successful dict() for completed registration'''
        activation_result = self.app.activate(self.douglas.email, self.confirmation_key)
        self.assertEquals({'successful': True}, activation_result)

    def test_failed_registration(self):
        '''Returns unsuccessful dict() for a bad activation'''
        activation_result = self.app.activate(self.douglas.email, 'bad_key')
        self.assertEquals({'successful': False}, activation_result)

    def test_user_marked_as_registered(self):
        '''The user's entry in the database is recorded as registered'''
        self.app.activate(self.douglas.email, self.confirmation_key)
        user_entry = self.bucket.documents[self.douglas.email]
        self.assertTrue(user_entry['registration_complete'])


class FakeMailer:
    def send(self, *args):
        pass

class MailerSpy:
    def __init__(self):
        self.to = None
        self.body = None

    def send(self, from_address, from_line, to, subject, body):
        self.to = to
        self.body = body


if __name__ == '__main__':
    unittest.main()
