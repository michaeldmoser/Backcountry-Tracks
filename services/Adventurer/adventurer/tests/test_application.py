import unittest
import types

from tptesting import environment

from adventurer.application import Application
from tptesting.fakeriak import RiakBucketFake
from uuid import uuid4

class TestApplication(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_registration_is_saved(self):
        """The registration is saved to Riak"""
        environ = environment.create()
        riakspy = RiakBucketSpy()
        fakemail = FakeMailer()

        app = Application(bucket = riakspy, mailer = fakemail)
        def confirmation_key_generator():
            return 'generated_confirmation_key'
        app.generate_confirmation_key = confirmation_key_generator

        user = environ.albert.copy()
        app.register(user)
        expected_data = user
        expected_data['confirmation_key'] = 'generated_confirmation_key'

        expected = {
                'key': environ.albert['email'],
                'data': expected_data
                }
        actual = {
                'key': riakspy.key,
                'data': riakspy.data
                }

        self.assertEquals(actual, expected)

    def test_registration_casts_unicode_email_to_string(self):
        """Registration allows Unicode emails"""
        environ = environment.create()
        riakspy = RiakBucketSpy()
        fakemail = FakeMailer()

        app = Application(bucket = riakspy, mailer = fakemail)
        user = environ.albert.copy()
        user['email'] = unicode('email@test.com')
        app.register(user)

        self.assertEquals(type(riakspy.key), types.StringType)

    def test_registration_sends_confirmation_email(self):
        """Registration sends confirmation email"""
        environ = environment.create()
        fakebucket = RiakBucketFake(None, None)
        mailerspy = MailerSpy()

        app = Application(bucket = fakebucket, mailer = mailerspy)
        user = environ.albert.copy()
        app.register(user)

        self.assertTrue(mailerspy.to, user['email'])

    def test_confirmation_email_contains_link_with_confirmation_key(self):
        """Registration email contains confirmation key"""
        environ = environment.create()

        riakspy = RiakBucketSpy()
        mailerspy = MailerSpy()
        trailhead_url = environ.get_config_for('trailhead_url');

        app = Application(
                bucket = riakspy,
                mailer = mailerspy,
                trailhead_url = trailhead_url
                )

        def confirmation_key_generator():
            return 'generated_confirmation_key'
        app.generate_confirmation_key = confirmation_key_generator
        user = environ.albert.copy()
        app.register(user)

        expected_link = '%s/activate/%s/%s' % (
                trailhead_url,
                user['email'],
                'generated_confirmation_key'
                )

        self.assertIn(expected_link, mailerspy.body)

class RiakBucketSpy(object):
    def new(spy, key, data=None):
        class RiakObjectSpy(object):
            def store(rspy):
                spy.key = key
                spy.data = data
        return RiakObjectSpy()

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
