from uuid import uuid4
from defer import Deferred
from .documents import KeyValueDocument

class Realm(object):
    def __init__(self, riak, name):
        self.riak = riak
        self.name = name
        self.bucket = self.riak.bucket(name)

    def get(self, key):
        robj = self.bucket.get(str(key))
        if not robj.exists():
            return None

        return KeyValueDocument(robj)

    def store(self, document):
        document.__object__.store()
        return document

    def delete(self, key):
        robj = self.bucket.get(str(key))
        if not robj.exists():
            return None

        robj.delete()
        

    def Document(self, key=None):
        key = str(key) if key is not None else str(uuid4())
        doc = self.bucket.new(key)
        return KeyValueDocument(doc)

