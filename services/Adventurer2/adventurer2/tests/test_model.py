import unittest

from tptesting import fakeriak, environment

from adventurer2.model import AdventurerRepository

class TestAdventurerRepositoryGet(unittest.TestCase):

    def test_returns_requested_user(self):
        '''Should return requested user'''
        bucket_name = 'adventurer'
        environ = environment.create()
        riakclient = fakeriak.RiakClientFake()
        riakclient()
        adventurer_bucket = riakclient.bucket(bucket_name)
        adventurer_bucket.add_document(environ.ramona.email, environ.ramona)

        adventurer = AdventurerRepository(riakclient, bucket_name)

        user = adventurer.get(environ.ramona.email)
        self.assertEquals(environ.ramona, user)

    def test_no_document_exists(self):
        '''No such document'''
        bucket_name = 'adventurer'
        environ = environment.create()
        riakclient = fakeriak.RiakClientFake()
        riakclient()
        riakclient.bucket(bucket_name) # make sure the bucket is created

        adventurer = AdventurerRepository(riakclient, bucket_name)
        user = adventurer.get(environ.ramona.email)
        self.assertIsNone(user)

if __name__ == '__main__':
    unittest.main()

