from uuid import uuid4
from defer import Deferred
from .documents import KeyValueDocument

# This may look weird returning a deferred that doesn't
# actually defer anything but the intent is to have an
# asynchronous api from the get go so when async operations are
# added users will not have to change their code.

class Realm(object):
    def __init__(self, riak, name):
        self.riak = riak
        self.name = name
        self.bucket = self.riak.bucket(name)

    def get(self, key):
        robj = self.bucket.get(str(key))

        deferred = Deferred()
        if not robj.exists():
            deferred.callback(None) 
        else:
            deferred.callback(KeyValueDocument(robj))

        return deferred

    def store(self, document):
        document.__object__.store()

    def Document(self):
        doc = self.bucket.new(str(uuid4()))

        return KeyValueDocument(doc)

