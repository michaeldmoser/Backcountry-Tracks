import unittest
import urllib2

from uuid import uuid4
import json

from tptesting import environment

class TestTripsServiceCreate(unittest.TestCase):

    def get_sut_trip(self):
        trip_list_request = urllib2.Request(self.trip_url)
        response = self.login_session.open(trip_list_request)
        trips = json.loads(response.read())

        return trips[0]

    def create_request(self, url, data = None, method = 'GET'):
        json_data = None if data is None else json.dumps(data)
        trip_request = urllib2.Request(
                self.trip_url + url,
                data = json_data
                )
        trip_request.get_method = lambda: method

        return trip_request

    def do_request(self, url, data = None, method = 'GET'):
        request = self.create_request(url, data = data, method = method)
        self.response = self.login_session.open(request)
        body = self.response.read()
        if len(body) < 1:
            return None

        data = json.loads(body)

        return data

    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()

        trips = cls.environ.trips
        albert = cls.environ.albert
        cls.user = cls.environ.create_user(albert)


        cls.trip = {
                'route_description': '',
                'trip_distance': '',
                'elevation_gain': '',
                'difficulty': '',
                'name': 'Test 1',
                'description': 'Test trip 1',
                'start': '2012-12-01',
                'end': '2012-12-05'
                }

        cls.trip_url = cls.environ.trailhead_url + '/trips'

        cls.login_session = albert.login()

    def setUp(self):
        self.environ.trips.remove_all()
        self.created_trip = self.do_request('', data = self.trip, method = 'POST')
        trip_id = self.created_trip['id']
        self.comment_url = "/%s/comments" % trip_id

    def post_the_comment(self, comment):
        self.do_request(self.comment_url, comment, method = 'POST')

    def get_stored_comment(self):
        comments = self.do_request(self.comment_url,  method = 'GET')
        return comments[0]

    def test_comment_on_trip(self):
        '''Post a comment to a trip'''
        comment = {'comment': 'The first comment'}
        
        self.post_the_comment(comment)
        stored_comment = self.get_stored_comment()
        self.assertDictContainsSubset(comment, stored_comment)


if __name__ == '__main__':
    unittest.main()


