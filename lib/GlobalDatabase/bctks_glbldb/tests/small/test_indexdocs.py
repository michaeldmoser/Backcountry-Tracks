import unittest
import copy
from tptesting.testcases import RiakFakeTestCase
import uuid

from bctks_glbldb.indexdocs import IndexDoc

class TestIndexDocs(RiakFakeTestCase):
    BUCKET = 'test'

    def test_retrieve_indexdoc(self):
        '''Retrieve an empty the index doc from the database'''
        index_doc = IndexDoc(self.adventurer, self.riak, self.BUCKET)
        self.assertEquals(index_doc, [])

    def test_retrieve_non_empty(self):
        '''Retrieve a non-empty index doc'''
        document = {
                'documents': [ str(uuid.uuid4()), str(uuid.uuid4()) ]
                }

        self.bucket.add_document(self.adventurer, document)
        index_doc = IndexDoc(self.adventurer, self.riak, self.BUCKET)
        self.assertEquals(index_doc, document['documents'])

    def test_add_key(self):
        '''Add a key to the index document'''
        key = str(uuid.uuid4())
        index_doc = IndexDoc(self.adventurer, self.riak, self.BUCKET)
        index_doc.append(key)
        index_doc.store()

        document = self.bucket.documents[self.adventurer]
        self.assertEquals(index_doc, document['documents'])

    def test_remove_key(self):
        '''Remove a key from the document list'''
        key1 = str(uuid.uuid4())
        key2 = str(uuid.uuid4())
        document = {'documents': [ key1, key2 ]}

        self.bucket.add_document(self.adventurer, document)
        index_doc = IndexDoc(self.adventurer, self.riak, self.BUCKET)
        index_doc.pop(0)
        index_doc.store()

        stored_document = self.bucket.documents[self.adventurer]
        expected_document = {'documents': [ key2 ]}
        self.assertEquals(stored_document, expected_document)






if __name__ == '__main__':
    unittest.main()

