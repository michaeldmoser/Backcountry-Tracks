
class KeyValueDocument(dict):
    def __init__(self, riak_object):
        self.__riak_object = riak_object
        data = self.__riak_object.get_data()
        if data is not None:
            dict.__init__(self, data)

        usermeta_defaults = {'object_type': 'generic'}
        usermeta = self.__riak_object.get_usermeta()
        usermeta_defaults.update(usermeta)
        self.__riak_object.set_usermeta(usermeta_defaults)

    @property
    def __object__(self):
        self.__riak_object.set_data(self)
        return self.__riak_object

    @property
    def key(self):
        return self.__riak_object.get_key()

    def __get_object_type(self):
        return self.__riak_object.get_usermeta().get('object_type', 'generic')

    def __set_object_type(self, value):
        usermeta = self.__riak_object.get_usermeta()
        usermeta.update({'object_type': value})
        self.__riak_object.set_usermeta(usermeta)

    object_type = property(fget=__get_object_type, fset=__set_object_type)

