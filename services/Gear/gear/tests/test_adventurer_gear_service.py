import unittest

import uuid

from bctks_glbldb.connection import Connection

from tptesting.fakeriak import RiakClientFake
from tptesting import environment

from gear.tests import utils

from gear.objects import AdventurerInventory
from gear.service import AdventurerGearService

class TestAdventuerGearServiceList(utils.AdventureInventoryTestCase):

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
        inventory = AdventurerInventory(self.realm, self.adventurer)

        def create_gear_list(gearpiece):
            piece_of_gear = inventory.PieceOfGear(gearpiece)
            inventory.add_gear(piece_of_gear)
            return piece_of_gear
        self.expected_list = map(create_gear_list, gear_list)

        def inventory_generator(owner):
            return AdventurerInventory(self.realm, owner)
        self.service = AdventurerGearService(inventory_generator)

    def test_list_of_gear(self):
        '''Retrieve list of gear for user'''
        retrieved_list = self.service.list(self.adventurer)
        self.assertEquals(self.expected_list, retrieved_list)

    def test_list_of_gear_with_missing(self):
        '''Retrieve list of gear for user where index contain missing objects'''
        obj = self.bucket.get(self.expected_list[0]['id'])
        obj.delete()
        del self.expected_list[0]

        retrieved_list = self.service.list(self.adventurer)
        self.assertEquals(self.expected_list, retrieved_list)
        
if __name__ == "__main__":
    unittest.main()

