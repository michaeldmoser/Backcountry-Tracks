import unittest

import urllib2
import json

from tptesting import environment, utils

class RetrieveGearList(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()


        gear = cls.environ.gear
        albert = cls.environ.albert
        cls.environ.create_user(albert)

        gear.add_item(albert.email, 'Alcohol Stove', 'Stove that burns alcohol', '2');
        gear.add_item(albert.email, 'Backpack', 'Backpack for carrying things', '37');
        gear.add_item(albert.email, 'Tarp', 'For shelter', '18');

        login_session = albert.login() 

        gear_list_url = cls.environ.trailhead_url + '/' + albert.email + '/gear'
        gear_list_request = urllib2.Request(
                gear_list_url
                )

        cls.response = login_session.open(gear_list_request)
        body = response.read()
        cls.gear_list = json.load(body)

    def test_list_of_gear_has_stove(self):
        """Test /app/<user>/gear returns a list of gear with a stove in it"""
        stove = {
                'name': 'Alcohol Stove',
                'description': 'Stove that burns alcohol',
                'weight': '2'
                }
        self.assertIn(stove, cls.gear_list)

    def test_list_of_gear_has_backpack(self):
        """Test /app/<user>/gear returns a list of gear with a backpack in it"""
        backpack = {
                'name': 'Backpack',
                'description': 'Backpack for carrying things',
                'weight': '37'
                }
        self.assertIn(backpack, cls.gear_list)

if __name__ == '__main__':
    unittest.main()