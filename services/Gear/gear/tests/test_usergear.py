import unittest

import uuid

from tptesting.fakeriak import RiakClientFake

from gear.usergear import UserGear

class TestUserGearList(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_list(self):
        """get list of gear"""
        owner = 'bob@smith.com'
        gearlist = [
                {'name': 'blah', 'description': 'bleh', 'weight': 'hi', 'owner': 'bob@smith.com'},
                {'name': 'blah1', 'description': 'bleh', 'weight': 'hi', 'owner': 'bob@smith.com'},
                {'name': 'blah2', 'description': 'bleh', 'weight': 'hi', 'owner': 'bob@smith.com'},
                ]

        riak = RiakClientFake()
        riak.add_mapreduce_result(gearlist, UserGear.list_mapreduce, 
                {'arg': {'owner': owner}})

        gear = UserGear(riak(), 'gear')

        actual_list = gear.list(owner)
        self.assertEquals(gearlist, actual_list)


class TestUserGearCreate(unittest.TestCase):

    def setUp(self):
        self.owner = 'bob@smith.com'
        self.pieceofgear = {
                'name': 'blah',
                'description': 'bleh',
                'weight': 'hi',
                }

        riak = RiakClientFake()
        self.bucket = riak.bucket('gear')

        self.gear_result = self.pieceofgear.copy()
        self.gear_result.update({'owner': self.owner})

        gear = UserGear(riak(), 'gear')
        self.result = gear.create(self.owner, self.pieceofgear)

    def test_create_gear(self):
        '''Creating a new piece gear saves to database'''
        document = self.bucket.documents.values()[0]
        self.assertDictContainsSubset(self.pieceofgear, document)

    def test_should_have_id(self):
        '''The return should have an ID key'''
        self.assertIn('id', self.result)

    def test_should_have_owner(self):
        '''Updated gear object returned'''
        self.assertDictContainsSubset(self.gear_result, self.result)

    def test_key_id(self):
        '''The riak object key and the gear id shoudl be the same'''
        key = self.bucket.documents.keys()[0]
        id = self.result['id']
        self.assertEquals(key, id)

class TestUserGearUpdate(unittest.TestCase):

    def setUp(self):
        self.owner = 'bob@smith.com'
        self.pieceofgear = {
                'name': 'blah',
                'description': 'bleh',
                'weight': 'hi',
                'owner': self.owner,
                'id': str(uuid.uuid4()),
                }

        riak = RiakClientFake()
        self.bucket = riak.bucket('gear')
        self.bucket.add_document(self.pieceofgear['id'], self.pieceofgear)

        self.gear_result = self.pieceofgear.copy()
        self.gear_result['name'] = 'booya'

        gear = UserGear(riak(), 'gear')
        self.result = gear.update(self.owner, self.pieceofgear['id'], self.gear_result)

    def test_update_gear(self):
        '''Updating a piece gear saves to database'''
        document = self.bucket.documents.values()[0]
        self.assertEquals(self.gear_result, document)

    def test_key_id(self):
        '''The riak object key and the gear id should be the same'''
        key = self.bucket.documents.keys()[0]
        id = self.result['id']
        self.assertEquals(key, id)


if __name__ == '__main__':
    unittest.main()

