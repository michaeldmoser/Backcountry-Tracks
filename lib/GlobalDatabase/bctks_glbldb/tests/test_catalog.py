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
        
        inventory.store_item(self.piece_of_gear)


    def test_store_item_to_inventory(self):
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

class TestCatalogUpdate(RiakFakeTestCase):
    BUCKET = 'gear'

    def continueSetup(self):
        self.inventory = Catalog(self.realm, self.adventurer, object_type = self.BUCKET)

        self.gear_data = {
                'name': 'Test',
                'weight': '1',
                'weight_unit': 'oz',
                'make': 'MSR',
                'model': 'Test',
                'description': 'The description',
                }
        self.piece_of_gear = self.inventory.Item(self.gear_data)
        
        self.inventory.store_item(self.piece_of_gear)
        self.piece_of_gear['name'] = 'Test 2'

    def test_update_item(self):
        '''Item gets updated'''
        self.inventory.store_item(self.piece_of_gear)
        riak_doc = self.bucket.documents[self.piece_of_gear.key]
        self.assertEquals(riak_doc['name'], self.piece_of_gear['name'])

    def test_update_item_only_one_index(self):
        self.inventory.store_item(self.piece_of_gear)
        index_doc = self.bucket.documents[self.adventurer]
        self.assertEquals(1, len(index_doc['documents']))


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
            self.inventory.store_item(piece_of_gear)
            return piece_of_gear
        self.gear_list = map(create_gear_list, gear_list)

    def test_delete_item(self):
        '''Delete an item from the catalog'''
        self.inventory.delete(self.gear_list[0]['id'])

        temp_gear_list = copy.deepcopy(self.gear_list)
        del temp_gear_list[0]
        expected_gear_list = sorted(temp_gear_list)
        docs = copy.deepcopy(self.bucket.documents)
        del docs[self.adventurer]
        actual = sorted(docs.values())
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

