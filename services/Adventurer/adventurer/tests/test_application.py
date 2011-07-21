import unittest
import types

from tptesting import environment

from adventurer.application import Application
from tptesting.fakeriak import RiakBucketFake, RiakClientFake

class TestApplication(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_registration_is_saved(self):
        """The registration is saved to Riak"""
        environ = environment.create()

        class RiakBucketSpy(object):
            def new(spy, key, data=None):
                class RiakObjectSpy(object):
                    def store(rspy):
                        spy.key = key
                        spy.data = data
                return RiakObjectSpy()
        riakspy = RiakBucketSpy()

        app = Application(bucket = riakspy)
        app.register(environ.albert)

        expected = {
                'key': environ.albert['email'],
                'data': environ.albert
                }
        actual = {
                'key': riakspy.key,
                'data': riakspy.data
                }

        self.assertEquals(actual, expected)

    def test_registration_casts_unicode_email_to_string(self):
        """Registration allows Unicode emails"""
        environ = environment.create()

        class RiakBucketSpy(object):
            def new(spy, key, data=None):
                class RiakObjectSpy(object):
                    def store(rspy):
                        spy.key = key
                        spy.data = data
                return RiakObjectSpy()
        riakspy = RiakBucketSpy()

        app = Application(bucket = riakspy)
        user = environ.albert.copy()
        user['email'] = unicode('email@test.com')
        app.register(user)

        self.assertEquals(type(riakspy.key), types.StringType)



if __name__ == '__main__':
    unittest.main()
