
class KeyValueDocument(dict):
    def __init__(self, riak_object):
        self._riak_object = riak_object
        data = self._riak_object.get_data()
        if data is not None:
            dict.__init__(self, data)

        self['id'] = self._riak_object.get_key()

        usermeta_defaults = {'object_type': 'generic'}
        usermeta = self._riak_object.get_usermeta()
        usermeta_defaults.update(usermeta)
        self._riak_object.set_usermeta(usermeta_defaults)

    @property
    def __object__(self):
        self._riak_object.set_data(self)
        return self._riak_object

    @property
    def key(self):
        return self._riak_object.get_key()

    def _get_object_type(self):
        return self._riak_object.get_usermeta().get('object_type', 'generic')

    def _set_object_type(self, value):
        usermeta = self._riak_object.get_usermeta()
        usermeta.update({'object_type': value})
        self._riak_object.set_usermeta(usermeta)

    object_type = property(fget=_get_object_type, fset=_set_object_type)

    def store(self):
        self._riak_object.store()

