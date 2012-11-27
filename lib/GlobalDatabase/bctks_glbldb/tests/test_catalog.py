import unittest
import copy
from tptesting.testcases import RiakFakeTestCase
import uuid

from bctks_glbldb.catalog import Catalog

class TestCatalogCreate(RiakFakeTestCase):
    BUCKET = 'gear'

    def continueSetup(self):
        inventory = Catalog(self.realm, self.adventurer, object_type = self.BUCKET)

        self.piece_of_gear = inventory.Item({
                'name': 'Test',
                'weight': '1',
                'weight_unit': 'oz',
                'make': 'MSR',
                'model': 'Test',
                'description': 'The description',
                })
        
        inventory.add_item(self.piece_of_gear)


    def test_add_item_to_inventory(self):
        '''Adding to inventory saves gear document to database'''
        riak_doc = self.bucket.documents[self.piece_of_gear.key]
        self.assertDictContainsSubset(self.piece_of_gear, riak_doc)

    def test_object_type_set_to_gear(self):
        '''object_type of usermeta should be gear'''
        riak_doc = self.bucket.documents[self.piece_of_gear.key]
        self.assertEquals(riak_doc.metadata['usermeta']['object_type'], self.BUCKET)

    def test_gear_added_to_index(self):
        '''The gear should be added to the adventurers gear index'''
        riak_doc = self.bucket.documents[self.adventurer]
        self.assertIn(self.piece_of_gear.key, riak_doc['documents'])

class TestCatalogList(RiakFakeTestCase):
    BUCKET = 'gear'

    def continueSetup(self):
        gear_list = [
                {
                    'make': 'MSR Whipserlite International',
                    'weight': '15',
                    'weight_unit': 'oz',
                    'description': 'test',
                    },
                {
                    'make': 'Whipserlite International',
                    'weight': '15',
                    'weight_unit': 'oz',
                    'description': 'test',
                    },
                {
                    'make': 'International',
                    'weight': '15',
                    'weight_unit': 'oz',
                    'description': 'test',
                    },
                ]
        self.inventory = Catalog(self.realm, self.adventurer, object_type = self.BUCKET)

        def create_gear_list(gearpiece):
            piece_of_gear = self.inventory.Item(gearpiece)
            self.inventory.add_item(piece_of_gear)
            return piece_of_gear
        self.expected_list = map(create_gear_list, gear_list)

    def test_list_of_gear(self):
        '''Return the list of gear'''
        gearlist = self.inventory.list_items()
        self.assertEquals(self.expected_list, gearlist)

    def test_piece_of_gear_missing(self):
        '''The index contains a reference not in the database'''
        obj = self.bucket.get(self.expected_list[0]['id'])
        obj.delete()
        del self.expected_list[0]

        retrieved_list = self.inventory.list_items()
        self.assertEquals(self.expected_list, retrieved_list)


class TestCatalogListEmpty(RiakFakeTestCase):
    BUCKET = 'gear'

    def test_empty_list(self):
        '''Index has not items'''
        index_doc = {'documents': []}
        obj = self.bucket.new(self.adventurer, index_doc)
        obj.store()

        inventory = Catalog(self.realm, self.adventurer, object_type=self.BUCKET)
        gearlist = inventory.list_items()

        self.assertEquals([], gearlist)

    def test_no_index(self):
        '''There is no gear index for the adventurer'''
        inventory = Catalog(self.realm, self.adventurer, object_type=self.BUCKET)
        gearlist = inventory.list_items()

        self.assertEquals([], gearlist)

class TestCatalogDeleteItem(RiakFakeTestCase):
    BUCKET = 'gear'

    def continueSetup(self):
        gear_list = [
                {
                    'make': 'MSR Whipserlite International',
                    'weight': '15',
                    'weight_unit': 'oz',
                    'description': 'test',
                    },
                {
                    'make': 'Whipserlite International',
                    'weight': '15',
                    'weight_unit': 'oz',
                    'description': 'test',
                    },
                {
                    'make': 'International',
                    'weight': '15',
                    'weight_unit': 'oz',
                    'description': 'test',
                    },
                ]
        self.inventory = Catalog(self.realm, self.adventurer, object_type = self.BUCKET)

        def create_gear_list(gearpiece):
            piece_of_gear = self.inventory.Item(gearpiece)
            self.inventory.add_item(piece_of_gear)
            return piece_of_gear
        self.gear_list = map(create_gear_list, gear_list)

    def test_delete_item(self):
        '''Delete an item from the catalog'''
        self.inventory.delete(self.gear_list[0]['id'])

        temp_gear_list = copy.deepcopy(self.gear_list)
        del temp_gear_list[0]
        expected_gear_list = sorted(temp_gear_list)
        actual = sorted(self.inventory.list_items())
        self.assertEquals(expected_gear_list, actual)

    def test_delete_index_document(self):
        '''Delete should remove item id from index document'''
        self.inventory.delete(self.gear_list[0]['id'])

        index_doc = self.bucket.documents[self.adventurer]
        self.assertNotIn(self.gear_list[0]['id'], index_doc['documents'])

    def test_delete_non_existant_item(self):
        '''Delete an item that doesn't exist should do nothing'''
        self.inventory.delete(str(uuid.uuid4()))



if __name__ == "__main__":
    unittest.main()

