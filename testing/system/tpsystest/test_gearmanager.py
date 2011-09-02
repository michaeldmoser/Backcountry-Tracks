import unittest

import urllib2
import json
import uuid

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

        gear_list_url = cls.environ.trailhead_url + '/users/' + albert.email + '/gear'
        gear_list_request = urllib2.Request(
                gear_list_url
                )

        cls.response = login_session.open(gear_list_request)
        body = cls.response.read()
        cls.gear_list = json.loads(body)

    def notest_list_of_gear_has_stove(self):
        """Test /app/users/<user>/gear returns a list of gear with a stove in it"""
        stove = {
                'name': 'Alcohol Stove',
                'description': 'Stove that burns alcohol',
                'weight': '2',
                'owner': 'albert.corley@example.com'
                }
        self.assertIn(stove, self.gear_list)

    def notest_list_of_gear_has_backpack(self):
        """Test /app/users/<user>/gear returns a list of gear with a backpack in it"""
        backpack = {
                'name': 'Backpack',
                'description': 'Backpack for carrying things',
                'weight': '37',
                'owner': 'albert.corley@example.com'
                }
        self.assertIn(backpack, self.gear_list)

class AddPieceOfGear(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()


        gear = cls.environ.gear
        albert = cls.environ.albert
        cls.environ.create_user(albert)

        login_session = albert.login() 

        cls.new_peice_of_gear = {
                'name': 'Hard Shell Jacket',
                'description': 'Wind / Rain proof jacket',
                'weight': '19',
                }

        gear_list_url = cls.environ.trailhead_url + '/users/' + albert.email + '/gear'
        gear_list_request = urllib2.Request(
                gear_list_url,
                data=json.dumps(cls.new_peice_of_gear),
                headers={'Content-Type': 'application/json'} 
                )

        cls.response = login_session.open(gear_list_request)
        body = cls.response.read()
        cls.response = json.loads(body)

    def notest_gear_item_id(self):
        '''Should receive the gear item back with an id added to the object'''
        self.assertIn('id', self.response)

    def notest_gear_item_owner(self):
        '''Should receive the gear item back with an id added to the object'''
        self.assertEquals(self.environ.albert.email, self.response['owner'])

    def notest_gear_in_database(self):
        '''The new piece of gear should be in the personal_gear database'''
        bucket = self.environ.riak.get_database('personal_gear')
        keys = bucket.get_keys()
        doc_object = bucket.get(str(keys[0]))
        pieceofgear = doc_object.get_data()

        self.assertDictContainsSubset(self.new_peice_of_gear, pieceofgear)


class EditPieceOfGear(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()


        gear = cls.environ.gear
        albert = cls.environ.albert
        cls.environ.create_user(albert)

        login_session = albert.login() 

        cls.old_gear = {
                'name': 'Hard Shell Jacket',
                'description': 'Wind / Rain proof jacket',
                'weight': '19',
                'owner': albert.email
                }

        cls.gear_id = cls.environ.gear.add_item(**cls.old_gear)
        cls.old_gear['id'] = cls.gear_id

        gear_url = cls.environ.trailhead_url + '/users/' + albert.email + \
                '/gear/' + cls.gear_id

        cls.updated_gear = {
                'name': 'Patagonia Torrent Shell',
                'description': 'Wind / Rain proof jacket',
                'weight': '19',
                'owner': albert.email
                }
        gear_list_request = urllib2.Request(
                gear_url,
                data=json.dumps(cls.updated_gear),
                headers={'Content-Type': 'application/json'} 
                )
        gear_list_request.get_method = lambda: 'PUT'

        cls.response = login_session.open(gear_list_request)
        body = cls.response.read()
        cls.response = json.loads(body)

    def notest_gear_item_returned(self):
        '''Should receive the gear item back'''
        self.assertEquals(self.updated_gear, self.response)

    def notest_gear_in_database(self):
        '''The new piece of gear should be in the personal_gear database'''
        bucket = self.environ.riak.get_database('personal_gear')
        keys = bucket.get_keys()
        doc_object = bucket.get(str(keys[0]))
        pieceofgear = doc_object.get_data()

        self.assertDictContainsSubset(self.updated_gear, pieceofgear)

class DeletePieceOfGear(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()


        gear = cls.environ.gear
        albert = cls.environ.albert
        cls.environ.create_user(albert)

        login_session = albert.login() 

        cls.gear = {
                'name': 'Hard Shell Jacket',
                'description': 'Wind / Rain proof jacket',
                'weight': '19',
                'owner': albert.email
                }

        cls.gear_id = cls.environ.gear.add_item(**cls.gear)

        gear_url = cls.environ.trailhead_url + '/users/' + albert.email + \
                '/gear/' + cls.gear_id

        gear_list_request = urllib2.Request(gear_url)
        gear_list_request.get_method = lambda: 'DELETE'

        cls.response = login_session.open(gear_list_request)

    def test_gear_item_returned(self):
        '''Should receive 204 no content'''
        self.assertEquals(204, self.response.code)

    def test_gear_in_database(self):
        '''The new piece of gear should be in the personal_gear database'''
        bucket = self.environ.riak.get_database('personal_gear')
        keys = bucket.get_keys()
        self.assertEquals([], keys)



if __name__ == '__main__':
    unittest.main()
