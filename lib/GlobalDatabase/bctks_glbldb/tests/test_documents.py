import unittest

from tptesting import fakeriak

from bctks_glbldb.connection import Connection
from bctks_glbldb.realm import Realm
from bctks_glbldb.documents import KeyValueDocument


class TestDocument(unittest.TestCase):

    def setUp(self):
        riak_client = fakeriak.RiakClientFake()
        self.bucket = riak_client.bucket('adventurers')

        conn = Connection(riak_client)
        self.realm = conn.Realm('adventurers') 
        self.document = self.realm.Document()
        self.document.update({'asdf': 'asdf'})
        self.realm.store(self.document)

    def test_get_object_type(self):
        '''Get an objects object_type'''
        object_type = self.document.object_type
        self.assertEquals('generic', object_type)

    def test_set_object_type(self):
        '''Set an objects object_type'''
        self.document.object_type = 'comment'
        self.realm.store(self.document)

        obj = self.bucket.get(self.document.key)
        self.assertDictContainsSubset({'object_type': 'comment'}, obj.get_usermeta())

    def test_save_default_object_type(self):
        '''object_type should default to generic when saved'''
        obj = self.bucket.get(self.document.key)
        self.assertDictContainsSubset({'object_type': 'generic'}, obj.get_usermeta())

    def test_save_key_as_id(self):
        '''The key should be saved in the document as id'''
        obj = self.bucket.get(self.document.key)
        self.assertEquals(obj.get_data()['id'], self.document.key)


if __name__ == '__main__':
    unittest.main()

