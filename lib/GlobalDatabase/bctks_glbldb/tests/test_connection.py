import unittest

from tptesting import fakeriak

from bctks_glbldb.connection import Connection
from bctks_glbldb.realm import Realm

class TestConnection(unittest.TestCase):

    def test_create_connection(self):
        '''Create a connection to the global database'''
        riak_client = fakeriak.RiakClientFake()
        Connection(riak_client)

    def test_retrieve_database_realm(self):
        '''Retrieve a database realm'''
        riak_client = fakeriak.RiakClientFake()
        conn = Connection(riak_client)

        realm = conn.Realm('adventurers') 

        self.assertIsInstance(realm, Realm)

        





if __name__ == '__main__':
    unittest.main()

