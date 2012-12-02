from uuid import uuid4
from defer import Deferred
from .documents import KeyValueDocument
from riak import RiakMapReduce, RiakObject

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

    def get_list(self, keys):
        mr = RiakMapReduce(self.riak)
        
        for key in keys:
            mr.add(self.name, key)

        map_js_function = '''
            function (v) 
            {
                var data = JSON.parse(v.values[0].data);
                data.id = v.key;
                return [data];
            }
            '''
        mr.map(map_js_function)

        results = mr.run()
        def make_kvdoc(item):
            riak_doc = RiakObject(self.riak, self.name, item['id'])
            riak_doc.set_data(item)
            kv_doc = KeyValueDocument(riak_doc)
            return kv_doc

        document_results = map(make_kvdoc, results)

        return document_results

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

