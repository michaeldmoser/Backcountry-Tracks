class Catalog(object):

    def __init__(self, realm, adventurer, object_type = "item"):
        self.realm = realm
        self.adventurer = adventurer
        self.object_type = object_type

    def Item(self, item_data):
        document = self.realm.Document()
        document.update(item_data)
        document.object_type = self.object_type
        return document

    def __get_item_index(self):
        index = self.realm.get(self.adventurer)

        if index is None:
            index_doc = self.realm.Document(key=self.adventurer)
            index_doc['documents'] = list()
            return index_doc

        return index

    def __add_item_to_index(self, item):
        index = self.__get_item_index()

        if not index.has_key('documents'):
            index['documents'] = list()
        index['documents'].append(item.key)
        self.realm.store(index)

    def add_item(self, item_document):
        self.realm.store(item_document)
        self.__add_item_to_index(item_document)

    def list_items(self):
        index = self.__get_item_index()

        potential_itemlist = map(lambda key: self.realm.get(key), index['documents'])
        final_itemlist = list()
        for pieceitem in potential_itemlist:
            if pieceitem is None:
                continue

            final_itemlist.append(pieceitem)
            
        return final_itemlist

