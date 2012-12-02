class Catalog(object):

    def __init__(self, realm, index_doc_id, object_type = "item"):
        self.realm = realm
        self.index_doc_id = index_doc_id
        self.object_type = object_type

    def Item(self, item_data):
        document = self.realm.Document()
        document.update(item_data)
        document.object_type = self.object_type
        return document

    def __get_item_index(self):
        index = self.realm.get(self.index_doc_id)

        if index is None:
            index_doc = self.realm.Document(key=self.index_doc_id)
            index_doc['documents'] = list()
            return index_doc

        return index

    def __add_item_to_index(self, item):
        index = self.__get_item_index()

        if not index.has_key('documents'):
            index['documents'] = list()

        if item.key in index['documents']:
            return

        index['documents'].append(item.key)
        self.realm.store(index)

    def __remove_item_from_index(self, key):
        index = self.__get_item_index()

        if not index.has_key('documents'):
            index['documents'] = list()

        try:
            index['documents'].remove(key)
        except ValueError:
            pass
        else:
            self.realm.store(index)

    def store_item(self, item_document):
        self.realm.store(item_document)
        self.__add_item_to_index(item_document)

    def list_items(self):
        index = self.__get_item_index()
        items = self.realm.get_list(index['documents'])
        return items

    def delete(self, key):
        self.realm.delete(key)
        self.__remove_item_from_index(key)


