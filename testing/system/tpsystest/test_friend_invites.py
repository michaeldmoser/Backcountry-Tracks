import unittest
import urllib2
import json

from tptesting import environment, utils

class InviteAFriend(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()

        cls.ramona = cls.environ.ramona
        cls.environ.create_user(cls.ramona)
        login_session = cls.ramona.login()

        cls.trip_data = cls.environ.trips.add_trips_to_user(cls.ramona, cls.environ.data['trips'])

        cls.trip_id = cls.trip_data[0]['id']
        trip_url = cls.environ.trailhead_url + "/trips/%s/friends" % cls.trip_id
        cls.invite_data = {
                'email': cls.environ.douglas.email,
                'first': cls.environ.douglas.first_name,
                'last': cls.environ.douglas.last_name,
                'invite_status': 'invited'
                }
        create_request = urllib2.Request(
                trip_url,
                data=json.dumps(cls.invite_data)
                )

        cls.create_response = login_session.open(create_request)
        body = cls.create_response.read()
        cls.response_body = json.loads(body)

    def test_friend_data_returned(self):
        '''Should return the trip data'''
        self.assertDictContainsSubset(self.invite_data, self.response_body)

    def test_friend_id(self):
        '''The response body should have an id listed'''
        self.assertIn('id', self.response_body)

    def test_friend_in_database(self):
        '''Make sure the friend is in the database'''
        bucket = self.environ.riak.get_database(self.environ.buckets['trips'])
        doc_object = bucket.get(str(self.trip_id))
        trip = doc_object.get_data()
        friend = trip['friends'][0]

        self.assertDictContainsSubset(self.invite_data, friend)

class AcceptAnInvite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()

        cls.ramona = cls.environ.ramona
        cls.environ.create_user(cls.ramona)
        login_session = cls.ramona.login()

        cls.trip_data = cls.environ.trips.add_trips_to_user(cls.ramona,
                cls.environ.data['trips'])
        cls.trip = cls.trip_data[0]
        cls.environ.trips.add_invitee(cls.trip['id'], cls.environ.douglas, 'invited')

        cls.trip_id = cls.trip_data[0]['id']
        trip_url = cls.environ.trailhead_url + "/trips/%s/friends/%s" % \
                (cls.trip_id, cls.environ.douglas.email)
        cls.invite_data = {
                'id': cls.environ.douglas.email,
                'email': cls.environ.douglas.email,
                'first': cls.environ.douglas.first_name,
                'last': cls.environ.douglas.last_name,
                'invite_status': 'accepted'
                }
        create_request = urllib2.Request(
                trip_url,
                data=json.dumps(cls.invite_data)
                )
        create_request.get_method = lambda: 'PUT'

        cls.create_response = login_session.open(create_request)
        #body = cls.create_response.read()
        #cls.response_body = json.loads(body)

    def test_invite_accepted(self):
        '''Accepting the invite should save to the database'''
        def check_in_database():
            trip = self.environ.trips.get(self.trip_id)
            douglas = self.environ.douglas
            invitee = filter(lambda friend: friend['email'] == douglas.email,
                    trip['friends'])[0]
            
            self.assertEquals('accepted', invitee['invite_status'])

        utils.try_until(3, check_in_database)
            

class IgnoreAnInvite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()

        cls.ramona = cls.environ.ramona
        cls.environ.create_user(cls.ramona)
        login_session = cls.ramona.login()

        cls.trip_data = cls.environ.trips.add_trips_to_user(cls.ramona,
                cls.environ.data['trips'])
        cls.trip = cls.trip_data[0]
        cls.environ.trips.add_invitee(cls.trip['id'], cls.environ.douglas, 'invited')

        cls.trip_id = cls.trip_data[0]['id']
        trip_url = cls.environ.trailhead_url + "/trips/%s/friends/%s" % \
                (cls.trip_id, cls.environ.douglas.email)
        cls.invite_data = {
                'id': cls.environ.douglas.email,
                'email': cls.environ.douglas.email,
                'first': cls.environ.douglas.first_name,
                'last': cls.environ.douglas.last_name,
                'invite_status': 'not coming'
                }
        create_request = urllib2.Request(
                trip_url,
                data=json.dumps(cls.invite_data)
                )
        create_request.get_method = lambda: 'PUT'

        cls.create_response = login_session.open(create_request)
        #body = cls.create_response.read()
        #cls.response_body = json.loads(body)

    def test_invite_accepted(self):
        '''Accepting the invite should save to the database'''
        def check_in_database():
            trip = self.environ.trips.get(self.trip_id)
            douglas = self.environ.douglas
            invitee = filter(lambda friend: friend['email'] == douglas.email,
                    trip['friends'])[0]
            
            self.assertEquals('not coming', invitee['invite_status'])

        utils.try_until(3, check_in_database)

        
if __name__ == '__main__':
    unittest.main()

