import unittest

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


        

if __name__ == '__main__':
    unittest.main()

