import pdb
import unittest
import defer

from tptesting import fakeriak

from bctks_glbldb.connection import Connection
from bctks_glbldb.realm import Realm
from bctks_glbldb.documents import KeyValueDocument

class TestDocumentStorageRetrieval(unittest.TestCase):

    def setUp(self):
        riak_client = fakeriak.RiakClientFake()

        self.document_key = '1234'
        self.saved_document = {'test': 'test', 'id': self.document_key}

        self.bucket = riak_client.bucket('adventurers')
        self.bucket.add_document(self.document_key, self.saved_document)
        conn = Connection(riak_client)
        self.realm = conn.Realm('adventurers') 

    def test_retrieve(self):
        '''Retrieve a document from a realm'''
        document = self.realm.get(self.document_key)
        self.assertEquals(dict(document), self.saved_document)

    def test_unicode_key(self):
        '''Realm.get() properly handles unicode based strings as a key'''
        document = self.realm.get(unicode(self.document_key))
        self.assertEquals(dict(document), self.saved_document)

    def test_keyvalue_document(self):
        '''Should return a KeyValueDocument when the content type is application/json'''
        document = self.realm.get(self.document_key)
        self.assertIsInstance(document, KeyValueDocument)

    def test_save_document(self):
        '''Save over a document'''
        document = self.realm.get(self.document_key)
        document['new'] = 'new'

        self.realm.store(document)

        saved_object = self.bucket.get(self.document_key)
        saved_data = saved_object.get_data()

        self.assertEquals(document, saved_data)

    def test_document_doesnt_exist(self):
        '''The request document doesn't exist'''
        document = self.realm.get('does not exist')
        self.assertIsNone(document)

class TestDocumentCreation(unittest.TestCase):
    def setUp(self):
        riak_client = fakeriak.RiakClientFake()

        conn = Connection(riak_client)
        self.realm = conn.Realm('adventurers') 

        self.document = self.realm.Document()
        self.document.update({
            'key1': 'value1',
            'key2': 'value2',
            })

        self.realm.store(self.document)

        self.bucket = riak_client.bucket('adventurers')
        obj = self.bucket.get(self.document.key)
        self.data = obj.get_data()

    def test_create_new_document(self):
        '''Realm() can create new document for storage directly in Riak'''
        self.assertEquals(self.data, self.document)

    def test_create_two_documents(self):
        '''Realm() can create new document for storage directly in Riak'''
        document2 = self.realm.Document()
        document2.update({
            'key3': 'value3',
            'key4': 'value4',
            })
        self.realm.store(document2)

        self.assertEquals(self.data, self.document1)

    def test_create_two_documents(self):
        '''Realm() can create new document for storage directly in Riak'''
        document2 = self.realm.Document()
        document2.update({
            'key3': 'value3',
            'key4': 'value4',
            })
        self.realm.store(document2)

        obj = self.bucket.get(document2.key)
        data = obj.get_data()

        self.assertEquals(data, document2)


class TestDocumentStorageRetrieval(unittest.TestCase):

    def setUp(self):
        riak_client = fakeriak.RiakClientFake()

        self.document_key = '1234'
        self.saved_document = {'test': 'test', 'id': self.document_key}

        self.bucket = riak_client.bucket('adventurers')
        self.bucket.add_document(self.document_key, self.saved_document)
        conn = Connection(riak_client)
        self.realm = conn.Realm('adventurers') 

    def test_delete(self):
        '''Remove a document from the database'''
        self.realm.delete(self.document_key)
        self.assertNotIn(self.saved_document, self.bucket.documents.keys())



if __name__ == '__main__':
    unittest.main()

