import unittest
import urllib2
from copy import deepcopy

from uuid import uuid4
import json

from riak import RiakClient

from tptesting import environment

from trips.coreservice import TripsCoreService
from trips.commentservice import TripCommentService

class TestTripsComments(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.riak.stop()
        cls.environ.riak.make_pristine()
        cls.environ.riak.start()

        cls.trips = cls.environ.data['trips']
        albert = cls.environ.albert
        cls.user = cls.environ.create_user(albert)

        cls.login_session = albert.login()
        cls.trip_url = cls.environ.trailhead_url + '/trips'
        cls.riak = RiakClient()

    def setUp(self):
        self.environ.trips.remove_all()

        self.comments = {
                str(uuid4()): {
                    'comment': 'The first comment',
                    },
                str(uuid4()): {
                    'comment': 'The second comment',
                    },
                }

        self.core = TripsCoreService(self.riak, 'trips')
        self.trip = self.core.create(self.user['key'], self.trips[0])

        trips_bucket = self.riak.bucket('trips')
        comments_bucket = self.riak.bucket('comments')

        trip_doc = trips_bucket.get(self.trip['id'])

        for key, comment in self.comments.items():
            comment_obj = comments_bucket.new(key, comment)
            comment_obj.store()
            trip_doc.add_link(comment_obj, 'comment')

        trip_doc.store()

        self.service = TripCommentService(self.riak, 'trips', 'comments')

    def test_list_comments(self):
        '''Retrieve list of comments on a trip'''
        comments = self.service.list(self.trip['id'])
        comments.sort()
        expected_comments = self.comments.values()
        expected_comments.sort()

        self.assertEquals(expected_comments, comments)

    def test_add_comment(self):
        '''Add a comment to a trip'''
        comment = {
                'comment': 'This is another comment',
                }
        self.service.add(self.trip['id'], comment)

        comments = self.service.list(self.trip['id'])
        comments.sort()

        expected_comments = self.comments.values()
        expected_comments.append(comment)
        expected_comments.sort()

        self.assertEquals(expected_comments, comments)


if __name__ == '__main__':
    unittest.main()

