from uuid import uuid4
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

    def Document(self):
        doc = self.bucket.new(str(uuid4()))

        return KeyValueDocument(doc)
        


