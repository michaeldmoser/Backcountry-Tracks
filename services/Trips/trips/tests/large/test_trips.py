import unittest
import urllib2

from uuid import uuid4
import json

from tptesting import environment

class TestTripsServiceCreate(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()

        trips = cls.environ.trips
        cls.albert = cls.environ.albert
        cls.user = cls.environ.create_user(cls.albert)
        cls.albert.login()


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

        cls.environ.trips.remove_all()
        cls.created_trip = cls.albert.do_request(cls.trip_url, data = cls.trip, method = 'POST')
        trip_id = cls.created_trip['id']
        cls.comment_url = "%s/%s/comments" % (cls.trip_url, trip_id)

        cls.comment = {'comment': 'The first comment'}
        cls.returned_comment = cls.albert.do_request(cls.comment_url, cls.comment, method = 'POST')

        comments = cls.albert.do_request(cls.comment_url,  method = 'GET')
        cls.stored_comment = comments[0]

    def test_comment_on_trip(self):
        '''The comment should be returned in the list of comments for a trip'''
        self.assertDictContainsSubset(self.comment, self.stored_comment)

    def test_date_recorded(self):
        '''The proper date/time is recorded on the comment'''
        assert self.stored_comment.has_key('date'), "Comment does not have date"

    def test_owner_on_comment(self):
        '''Check that the owner is listed on the comment'''
        assert self.stored_comment.has_key('owner'), 'There is no owner listed on the comment'

    def test_name_on_comment(self):
        '''Check that the name of the owner is in the comment'''
        name = {'first_name': self.albert.first_name, 'last_name': self.albert.last_name} 
        self.assertDictContainsSubset(name, self.stored_comment)



if __name__ == '__main__':
    unittest.main()


