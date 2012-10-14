import unittest

import uuid

from bctks_glbldb.connection import Connection

from tptesting.fakeriak import RiakClientFake
from tptesting import environment

from gear.objects import AdventurerInventory

class TestAdventurerInventoryCreate(unittest.TestCase):

    def setUp(self):
        environ = environment.create()
        riak = RiakClientFake()
        self.bucket = riak.bucket('personal_gear')
        dbcon = Connection(riak)
        realm = dbcon.Realm('personal_gear')

        self.adventurer = str(uuid.uuid4())

        inventory = AdventurerInventory(realm, self.adventurer)

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


if __name__ == "__main__":
    unittest.main()

