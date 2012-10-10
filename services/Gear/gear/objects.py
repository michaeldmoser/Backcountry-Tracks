from bctks_glbldb.documents import KeyValueDocument

class UserInventory(object):

    def __init__(self, realm, user):
        self.realm = realm
        self.user = user

    def PieceOfGear(self, gear_data):
        document = self.realm.Document()
        document.update(gear_data)
        document.object_type = 'gear'
        return document

    def __get_gear_index(self):
        index = self.realm.get(self.user)

        if index is None:
            return self.realm.Document(key=self.user)

        return index

    def __store_gear_index(self, index):
        self.realm.store(index)

    def __add_gear_to_index(self, gear):
        index = self.__get_gear_index()

        if not index.has_key('documents'):
            index['documents'] = list()
        index['documents'].append(gear.key)
        self.__store_gear_index(index)

    def add_gear(self, gear_document):
        self.realm.store(gear_document)
        self.__add_gear_to_index(gear_document)


