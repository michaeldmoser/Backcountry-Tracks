import unittest
import urllib2
import json

from tptesting import environment, utils

class TripPersonalGear(unittest.TestCase):

    def test_retrieve_personal_gear(self):
        '''Retrieve personal gear for a trip'''
        env = environment.create()
        env.make_pristine()
        env.bringup_infrastructure()

        douglas = env.douglas
        env.create_user(douglas)
        login_session = douglas.login()

        trips = env.trips.add_trips_to_user(douglas, env.data['trips'])
        gear = env.gear.add_gear_to_user(douglas, env.data['gear'])

        env.trips.add_trip_gear(douglas, trips[0]['id'], gear)

        url = env.trailhead_url + '/trips/%s/gear/personal' % trips[0]['id']
        response = login_session.open(url)
        gear_response = json.load(response)
        
        compare = lambda a, b: cmp(a['id'], b['id'])
        gear_response.sort(compare)
        gear.sort(compare)

        self.assertEquals(gear, gear_response)


class TripAddPersonalGear(unittest.TestCase):

    def setUp(self):
        env = environment.create()
        env.make_pristine()
        env.bringup_infrastructure()
        self.env = env

        douglas = env.douglas
        env.create_user(douglas)
        login_session = douglas.login()

        self.trips = env.trips.add_trips_to_user(douglas, env.data['trips'])
        self.gear = env.gear.add_gear_to_user(douglas, env.data['gear'])

        self.trip = self.trips[0]
        self.gear_item = self.gear[0]
        url = env.trailhead_url + '/trips/%s/gear/personal/%s' % \
                (self.trip['id'], self.gear_item['id'])
        gear_add_request = urllib2.Request(
                url,
                data=json.dumps(self.gear_item),
                headers={'Content-Type': 'application/json'} 
                )
        gear_add_request.get_method = lambda: 'PUT'

        self.response = login_session.open(gear_add_request)

    def test_add_personal_gear(self):
        '''Add gear to personal gear list for a trip'''
        def check_gear():
            trip = self.env.trips.get(self.trip['id'])
            gear = trip.get('gear', {}).get(self.env.douglas.email, [None])[0]
            self.assertEquals(gear, self.gear_item)

        utils.try_until(2, check_gear)

class TripRetrieveGroupGear(unittest.TestCase):

    def test_retrieve_group_gear(self):
        '''Retrieve group gear for a trip'''
        env = environment.create()
        env.make_pristine()
        env.bringup_infrastructure()

        douglas = env.douglas
        env.create_user(douglas)
        login_session = douglas.login()

        trips = env.trips.add_trips_to_user(douglas, env.data['trips'])
        gear = env.gear.add_gear_to_user(douglas, env.data['gear'])

        env.trips.add_group_gear(trips[0]['id'], gear)

        url = env.trailhead_url + '/trips/%s/gear/group' % trips[0]['id']
        response = login_session.open(url)
        gear_response = json.load(response)
        
        compare = lambda a, b: cmp(a['id'], b['id'])
        gear_response.sort(compare)
        gear.sort(compare)

        self.assertEquals(gear, gear_response)

class TripAddGroupGear(unittest.TestCase):

    def setUp(self):
        env = environment.create()
        env.make_pristine()
        env.bringup_infrastructure()
        self.env = env

        douglas = env.douglas
        env.create_user(douglas)
        login_session = douglas.login()

        self.trips = env.trips.add_trips_to_user(douglas, env.data['trips'])
        self.gear = env.gear.add_gear_to_user(douglas, env.data['gear'])

        self.trip = self.trips[0]
        self.gear_item = self.gear[0]
        url = env.trailhead_url + '/trips/%s/gear/group/%s' % \
                (self.trip['id'], self.gear_item['id'])
        gear_add_request = urllib2.Request(
                url,
                data=json.dumps(self.gear_item),
                headers={'Content-Type': 'application/json'} 
                )
        gear_add_request.get_method = lambda: 'PUT'

        self.response = login_session.open(gear_add_request)

    def test_add_group_gear(self):
        '''Share gear on a trip'''
        def check_gear():
            trip = self.env.trips.get(self.trip['id'])
            gear = trip.get('groupgear', [])
            self.assertIn(self.gear_item, gear)

        utils.try_until(2, check_gear)

if __name__ == '__main__':
    unittest.main()

