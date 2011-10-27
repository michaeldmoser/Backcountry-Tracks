import unittest
import types

from tptesting import environment

from adventurer.application import Application
from tptesting.fakeriak import RiakClientFake
from uuid import uuid4

class TestApplication(unittest.TestCase):
    def setUp(self):
        self.environ = environment.create()
        self.riak = RiakClientFake()
        self.fakemail = FakeMailer()

        self.bucket = self.riak.bucket('adventurer')

    def test_registration_is_saved(self):
        """The registration is saved to Riak"""
        app = Application(bucket = self.bucket, mailer = self.fakemail)
        def confirmation_key_generator():
            return 'generated_confirmation_key'
        app.generate_confirmation_key = confirmation_key_generator

        user = self.environ.albert.registration_data()
        app.register(user)
        expected_data = user
        expected_data['confirmation_key'] = 'generated_confirmation_key'

        riak_object = self.bucket.get(self.environ.albert['email'])
        actual_data = riak_object.get_data()

        self.assertEquals(actual_data, expected_data)

    def test_registration_casts_unicode_email_to_string(self):
        """Registration allows Unicode emails"""
        app = Application(bucket = self.bucket, mailer = self.fakemail)
        user = self.environ.albert.registration_data()
        user['email'] = unicode('email@test.com')
        app.register(user)

        riak_object = self.bucket.get('email@test.com')
        registered_user = riak_object.get_data()

        self.assertIsNotNone(registered_user)

    def test_registration_sends_confirmation_email(self):
        """Registration sends confirmation email"""
        mailerspy = MailerSpy()
        app = Application(bucket = self.bucket, mailer = mailerspy)
        user = self.environ.albert.registration_data()
        app.register(user)

        self.assertTrue(mailerspy.to, user['email'])

    def test_confirmation_email_contains_link_with_confirmation_key(self):
        """Registration email contains confirmation key"""
        trailhead_url = self.environ.get_config_for('trailhead_url');

        mailerspy = MailerSpy()
        app = Application(
                bucket = self.bucket,
                mailer = mailerspy,
                trailhead_url = trailhead_url
                )

        def confirmation_key_generator():
            return 'generated_confirmation_key'
        app.generate_confirmation_key = confirmation_key_generator
        user = self.environ.albert.copy()
        user['password_again'] = user['password']
        app.register(user)

        expected_link = '%s/activate/%s/%s' % (
                trailhead_url,
                user['email'],
                'generated_confirmation_key'
                )

        self.assertIn(expected_link, mailerspy.body)

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
