import unittest

from gear.objects import AdventurerInventory
from gear.tests import utils

class TestAdventurerInventoryCreate(utils.AdventureInventoryTestCase):

    def continueSetup(self):
        inventory = AdventurerInventory(self.realm, self.adventurer)

        self.piece_of_gear = inventory.PieceOfGear({
                'name': 'Test',
                'weight': '1',
                'weight_unit': 'oz',
                'make': 'MSR',
                'model': 'Test',
                'description': 'The description',
                })
        
        inventory.add_gear(self.piece_of_gear)


    def test_add_gear_to_inventory(self):
        '''Adding to inventory saves gear document to database'''
        riak_doc = self.bucket.documents[self.piece_of_gear.key]
        self.assertDictContainsSubset(self.piece_of_gear, riak_doc)

    def test_object_type_set_to_gear(self):
        '''object_type of usermeta should be gear'''
        riak_doc = self.bucket.documents[self.piece_of_gear.key]
        self.assertEquals(riak_doc.metadata['usermeta']['object_type'], 'gear')

    def test_gear_added_to_index(self):
        '''The gear should be added to the adventurers gear index'''
        riak_doc = self.bucket.documents[self.adventurer]
        self.assertIn(self.piece_of_gear.key, riak_doc['documents'])

class TestAdventurerInventoryList(utils.AdventureInventoryTestCase):

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
        self.inventory = AdventurerInventory(self.realm, self.adventurer)

        def create_gear_list(gearpiece):
            piece_of_gear = self.inventory.PieceOfGear(gearpiece)
            self.inventory.add_gear(piece_of_gear)
            return piece_of_gear
        self.expected_list = map(create_gear_list, gear_list)

    def test_list_of_gear(self):
        '''Return the list of gear'''
        gearlist = self.inventory.list_gear()
        self.assertEquals(self.expected_list, gearlist)

    def test_piece_of_gear_missing(self):
        '''The index contains a reference not in the database'''
        obj = self.bucket.get(self.expected_list[0]['id'])
        obj.delete()
        del self.expected_list[0]

        retrieved_list = self.inventory.list_gear()
        self.assertEquals(self.expected_list, retrieved_list)


class TestAdventurerInventoryListEmpty(utils.AdventureInventoryTestCase):

    def test_empty_list(self):
        '''Index has not items'''
        index_doc = {'documents': []}
        obj = self.bucket.new(self.adventurer, index_doc)
        obj.store()

        inventory = AdventurerInventory(self.realm, self.adventurer)
        gearlist = inventory.list_gear()

        self.assertEquals([], gearlist)

    def test_no_index(self):
        '''There is no gear index for the adventurer'''
        inventory = AdventurerInventory(self.realm, self.adventurer)
        gearlist = inventory.list_gear()

        self.assertEquals([], gearlist)

if __name__ == "__main__":
    unittest.main()

