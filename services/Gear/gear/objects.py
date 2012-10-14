from bctks_glbldb.documents import KeyValueDocument

class AdventurerInventory(object):

    def __init__(self, realm, adventurer):
        self.realm = realm
        self.adventurer = adventurer

    def PieceOfGear(self, gear_data):
        document = self.realm.Document()
        document.update(gear_data)
        document.object_type = 'gear'
        return document

    def __get_gear_index(self):
        index = self.realm.get(self.adventurer)

        if index is None:
            index_doc = self.realm.Document(key=self.adventurer)
            index_doc['documents'] = list()
            return index_doc

        return index

    def __add_gear_to_index(self, gear):
        index = self.__get_gear_index()

        if not index.has_key('documents'):
            index['documents'] = list()
        index['documents'].append(gear.key)
        self.realm.store(index)

    def add_gear(self, gear_document):
        self.realm.store(gear_document)
        self.__add_gear_to_index(gear_document)

    def list_gear(self):
        index = self.__get_gear_index()

        potential_gearlist = map(lambda key: self.realm.get(key), index['documents'])
        final_gearlist = list()
        for piecegear in potential_gearlist:
            if piecegear is None:
                continue

            final_gearlist.append(piecegear)
            
        return final_gearlist

