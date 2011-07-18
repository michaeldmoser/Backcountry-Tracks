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

class RiakClientFake(object):

    def __init__(self):
        self.__buckets = dict()

    def __call__(self, host='127.0.0.1', port=8098, prefix='riak',
                 mapred_prefix='mapred', transport_class=None,
                 client_id=None):
        self.host = host
        self.port = port
        self.prefix = prefix
        self.mapred_prefix = mapred_prefix
        self.transport_class = transport_class
        self.client_id = client_id

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
        raise NotImplementedError

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

    def add_document(self, key, data):
        '''
        Creates a document for retrieval by the SUT code
        '''
        self.__documents[key] = data

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
        obj.set_data(data)
        obj.set_content_type(content_type)
        obj._encode_data = True
        return obj

    def new_binary(self, key, data, content_type='application/octet-stream'):
		raise NotImplementedError

    def get(self, key, r=None):
        try:
            document = self.__documents[key]
        except KeyError:
            return RiakObjectFake(self.client, self)

        obj = RiakObjectFake(self.client, self, key=key)
        obj.set_data(document)
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
        self.key = key
        self.client = client
        self.bucket = bucket
        self._encode_data = False
        self.__data = None

        self._exists = False

    def get_bucket(self):
		raise NotImplementedError

    def get_key(self):
		raise NotImplementedError

    def get_data(self):
        return self.__data

    def set_data(self, data):
        self.__data = data

    def get_encoded_data(self):
		raise NotImplementedError

    def set_encoded_data(self, data):
		raise NotImplementedError

    def get_metadata(self):
		raise NotImplementedError

    def set_metadata(self, metadata):
		raise NotImplementedError

    def exists(self):
        return self._exists

    def get_content_type(self):
		raise NotImplementedError

    def set_content_type(self, content_type):
        self.content_type = content_type

    def add_link(self, obj, tag=None):
		raise NotImplementedError

    def remove_link(self, obj, tag=None):
		raise NotImplementedError

    def get_links(self):
		raise NotImplementedError

    def store(self, w=None, dw=None, return_body=True):
        self.bucket.documents[self.key] = self.data

    def reload(self, r=None, vtag=None):
		raise NotImplementedError

    def delete(self, rw=None):
		raise NotImplementedError

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

