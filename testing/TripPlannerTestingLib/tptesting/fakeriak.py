"""
Usage:

>>> client_class = RiakClientFake()

The SUT will then use the fake RiakClient like normal
>>> client = client_class(host='localhost', port=8098)
>>> client.bucket('adventurer')
...

Validating and verification in the test
>>> assert client_class.host == 'localhost'
>>> assert client_class.port == 8098

Checking the data
>>> bucket = client_class.bucket('adventurer')
>>> albert = bucket.documents['albert@example.com']
>>> self.assertEquals(albert, environ.albert)
"""

import uuid
from copy import deepcopy
from riak.mapreduce import RiakLink

class RiakDocument(dict):

    def __init__(self, *args, **kwargs):
        if len(args) > 0 and args[0] is not None:
            dict.__init__(self, *args, **kwargs)
        else:
            dict.__init__(self)

        self.metadata = {
                'content-type': 'application/json',
                'vtag': str(uuid.uuid4()),
                'lastmod': 'Sun, 29 Jan 2012 22:39:35 GMT',
                'links': list(),
                'usermeta': dict(),
                }

class RiakBinary(str):
    def __init__(self, data):
        str.__init__(self, data)
        self.metadata = {
                'content-type': 'application/json',
                'vtag': str(uuid.uuid4()),
                'lastmod': 'Sun, 29 Jan 2012 22:39:35 GMT',
                'links': list(),
                'usermeta': dict(),
                }


class RiakClientFake(object):

    def __init__(self):
        self.mr_result = {}
        self.__buckets = dict()

    def add_mapreduce_result(self, result, mapping, options=None):
        '''
        Add a result of a map/reduce operation that should be returned from RiakMapReduce.run()
        '''
        self.mr_result[mapping] = {
                'result': result,
                'options': options
                }

    def __call__(self, host='127.0.0.1', port=8098, prefix='riak',
                 mapred_prefix='mapred', transport_class=None,
                 client_id=None):
        self.host = host
        self.port = port
        self.prefix = prefix
        self.mapred_prefix = mapred_prefix
        self.transport_class = transport_class
        self.client_id = client_id
        return self


    def get_transport(self):
        raise NotImplementedError

    def get_r(self):
        raise NotImplementedError

    def set_r(self, r):
        raise NotImplementedError

    def get_w(self):
        raise NotImplementedError

    def set_w(self, w):
        raise NotImplementedError

    def get_dw(self):
        raise NotImplementedError

    def set_dw(self, dw):
        raise NotImplementedError

    def get_rw(self):
        raise NotImplementedError

    def set_rw(self, rw):
        raise NotImplementedError

    def get_client_id(self):
        raise NotImplementedError

    def set_client_id(self, client_id):
        raise NotImplementedError

    def get_encoder(self, content_type):
        raise NotImplementedError

    def set_encoder(self, content_type, encoder):
        raise NotImplementedError

    def get_decoder(self, content_type):
        raise NotImplementedError

    def set_decoder(self, content_type, decoder):
        raise NotImplementedError

    def bucket(self, name):
        if self.__buckets.has_key(name):
            return self.__buckets[name]

        self.__buckets[name] = RiakBucketFake(self, name)
        return self.__buckets[name]

    def is_alive(self):
        raise NotImplementedError

    def add(self, *args):
        mr = RiakMapReduceFake(self)
        mr.add_results(self.mr_result)
        return apply(mr.add, args)

    def search(self, *args):
        raise NotImplementedError

    def link(self, *args):
        raise NotImplementedError

    def map(self, *args):
        raise NotImplementedError

    def reduce(self, *args):
        raise NotImplementedError

class RiakBucketFake(object):
    @property
    def documents(self):
        '''
        Stores the documents in a dict() object
        '''
        return self.__documents

    def add_document(self, key, data, links=[]):
        '''
        Creates a document for retrieval by the SUT code
        '''
        document = RiakDocument(deepcopy(data))
        document.metadata['links'].extend(links)
        self.__documents[key] = document

    def __init__(self, client, name):
        self.name = name
        self.client = client
        self.__documents = dict()

    def get_name(self):
		raise NotImplementedError

    def get_r(self, r=None):
		raise NotImplementedError

    def set_r(self, r):
		raise NotImplementedError

    def get_w(self, w=None):
		raise NotImplementedError

    def set_w(self, w):
		raise NotImplementedError

    def get_dw(self, dw=None):
		raise NotImplementedError

    def set_dw(self, dw):
		raise NotImplementedError

    def get_rw(self, rw=None):
		raise NotImplementedError

    def set_rw(self, rw):
		raise NotImplementedError

    def get_encoder(self, content_type):
		raise NotImplementedError

    def set_encoder(self, content_type, encoder):
		raise NotImplementedError

    def get_decoder(self, content_type):
		raise NotImplementedError

    def set_decoder(self, content_type, decoder):
		raise NotImplementedError

    def new(self, key, data=None, content_type='application/json'):
        obj = RiakObjectFake(self.client, self, key)
        obj.set_content_type(content_type)
        if data is not None:
            obj.set_data(deepcopy(data))
        else:
            obj.set_data(data)
        obj._encode_data = True
        return obj

    def new_binary(self, key, data, content_type='application/octet-stream'):
        obj = RiakObjectFake(self.client, self, key)
        obj.set_content_type(content_type)
        if data is not None:
            obj.set_data(deepcopy(data))
        else:
            obj.set_data(data)
        obj._encode_data = True
        return obj

    def get(self, key, r=None):
        try:
            document = deepcopy(self.__documents[key])
        except KeyError:
            return RiakObjectFake(self.client, self)

        obj = RiakObjectFake(self.client, self, key=key)
        if isinstance(document, RiakBinary):
            obj.set_content_type('application/octet-stream')

        obj.set_data(document)
        obj.set_metadata(document.metadata)

        # in production this is not random data but for testing purposes this will work
        # for the time being
        obj._vclock = str(uuid.uuid4())
        obj._exists = True
        return obj


    def get_binary(self, key, r=None):
		raise NotImplementedError

    def set_n_val(self, nval):
		raise NotImplementedError

    def get_n_val(self):
		raise NotImplementedError

    def set_default_r_val(self, rval):
		raise NotImplementedError

    def get_default_r_val(self):
		raise NotImplementedError

    def set_default_w_val(self, wval):
		raise NotImplementedError

    def get_default_w_val(self):
		raise NotImplementedError

    def set_default_dw_val(self, dwval):
		raise NotImplementedError

    def get_default_dw_val(self):
		raise NotImplementedError

    def set_default_rw_val(self, rwval):
		raise NotImplementedError

    def get_default_rw_val(self):
		raise NotImplementedError

    def set_allow_multiples(self, bool):
		raise NotImplementedError

    def get_allow_multiples(self):
		raise NotImplementedError

    def set_property(self, key, value):
		raise NotImplementedError

    def get_bool_property(self, key):
		raise NotImplementedError

    def get_property(self, key):
		raise NotImplementedError

    def set_properties(self, props):
		raise NotImplementedError

    def get_properties(self):
		raise NotImplementedError

    def get_keys(self):
		raise NotImplementedError

class RiakObjectFake(object):
    def __init__(self, client, bucket, key=None):
        if isinstance(key, unicode):
            raise TypeError('Unicode keys are not supported.')

        self.key = key
        self.client = client
        self.bucket = bucket
        self._encode_data = False
        self.__data = None
        self.content_type = 'application/json'
        self._vclock = None

        self._exists = False

    def get_bucket(self):
		raise NotImplementedError

    def get_key(self):
        return self.key

    def get_data(self):
        return self.__data

    def set_data(self, data):
        if not isinstance(data, str) and not isinstance(data, dict) and data is not None:
            raise TypeError("You must use str()'s or dict()'s for data. The underlying pycurl library will reject it otherwise")

        if isinstance(self.__data, RiakDocument):
            self.__data.update(data)
            return

        if self.content_type == 'application/json':
            self.__data = RiakDocument(data)
        else:
            self.__data = RiakBinary(data)

    def get_encoded_data(self):
		raise NotImplementedError

    def set_encoded_data(self, data):
		raise NotImplementedError

    def get_metadata(self):
        return deepcopy(self.__data.metadata)

    def set_metadata(self, metadata):
        self.__data.metadata = deepcopy(metadata)
        return self

    def get_usermeta(self):
        if not self.__data:
            self.__data = RiakDocument()

        if 'usermeta' in self.__data.metadata:
          return deepcopy(self.__data.metadata['usermeta'])
        else:
          return {}

    def set_usermeta(self, usermeta):
        """
        Sets the custom user metadata on this object. This doesn't include things
        like content type and links, but only user-defined meta attributes stored
        with the Riak object.

        :param userdata: The user metadata to store.
        :type userdata: dict
        :rtype: data
        """
        if not self.__data:
            self.__data = RiakDocument()

        self.__data.metadata['usermeta'] = deepcopy(usermeta)
        return self

    def exists(self):
        return self._exists

    def get_content_type(self):
		raise NotImplementedError

    def set_content_type(self, content_type):
        self.content_type = content_type

    def add_link(self, obj, tag=None):
        if isinstance(obj, RiakLink):
            newlink = obj
        else:
            newlink = RiakLink(obj.bucket.name, obj.key, tag)

        newlink._client = self.client

        if not isinstance(self.__data, RiakDocument):
            self.__data = RiakDocument(self.__data)

        self.__data.metadata['links'].append(newlink)

    def remove_link(self, obj, tag=None):
		raise NotImplementedError

    def get_links(self):
        if not isinstance(self.__data, RiakDocument):
            return []

        return self.__data.metadata['links']

    def store(self, w=None, dw=None, return_body=True):
        if self.bucket.documents.has_key(self.key) and \
                self._vclock is None:
            self.__data = self.bucket.documents[self.key]
        else:
            self.bucket.documents[self.key] = self.__data

        self._exists = True

        return self

    def reload(self, r=None, vtag=None):
		raise NotImplementedError

    def delete(self, rw=None):
        del self.bucket.documents[self.key]

    def clear(self) :
		raise NotImplementedError

    def vclock(self) :
		raise NotImplementedError

    def populate(self, Result) :
		raise NotImplementedError

    def populate_links(self, linkHeaders):
		raise NotImplementedError

    def has_siblings(self):
		raise NotImplementedError

    def get_sibling_count(self):
		raise NotImplementedError

    def get_sibling(self, i, r=None):
		raise NotImplementedError

    def get_siblings(self, r=None):
		raise NotImplementedError

    def set_siblings(self, siblings):
		raise NotImplementedError

    def add(self, *args):
		raise NotImplementedError

    def link(self, *args):
		raise NotImplementedError

    def map(self, *args):
		raise NotImplementedError

    def reduce(self, params):
		raise NotImplementedError

class RiakMapReduceFake(object):
    ### These function are test helpers are not part of the Riak api
    def add_results(self, result):
        self.result = result

    #### The following functions are part of the core api for Riak
    def __init__(self, client):
        self.result = {}
        self.mapping_function = ''
        self.map_options = ''

    def add(self, arg1, arg2=None, arg3=None):
        return self

    def add_object(self, obj):
        raise NotImplementedError

    def add_bucket_key_data(self, bucket, key, data) :
        raise NotImplementedError

    def add_bucket(self, bucket) :
        raise NotImplementedError

    def search(self, bucket, query):
        raise NotImplementedError

    def link(self, bucket='_', tag='_', keep=False):
        raise NotImplementedError

    def map(self, function, options=None):
        self.mapping_function = function
        self.map_options = options
        return self

    def reduce(self, function, options=None):
        raise NotImplementedError

    def run(self, timeout=None):
        if not self.result.has_key(self.mapping_function):
            return []

        result = self.result[self.mapping_function]
        if self.map_options != result['options']:
            return []

        return result['result']


