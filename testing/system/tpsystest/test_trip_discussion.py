import unittest
import urllib2
import json
import pika
import os.path

from dateutil import parser, tz
import datetime

from tptesting import environment, utils, httputils

class TestPostComment(httputils.SystemTestFixture):

    @classmethod
    def postSetUpClass(cls):
        trip = cls.trips[0]
        url = '/trips/%s/comments' % trip['id']
        post_data = {
                'comment': 'This is a comment'
                }
        cls.stored_comment = cls.perform_request(url, post_data=post_data)

    def test_post_comment_to_trip(self):
        '''Comment post response should have owner and comment'''
        expected_response = {
                'owner': self.env.douglas.email,
                'comment': 'This is a comment'
                }
        self.assertDictContainsSubset(expected_response, self.stored_comment)

    def test_post_comment_date(self):
        '''Comment post response should have date equal to now'''
        now = datetime.datetime.now(tz.tzutc())
        comment_date = parser.parse(str(self.stored_comment.get('date', '')))

        time_delta = now - comment_date
        self.assertLess(time_delta.seconds, 5)

    def test_content_type(self):
        '''Comment post response content-type should be json'''
        contentype = self.response.headers['Content-Type']
        self.assertIn('application/json', contentype)

class TestGetComments(httputils.SystemTestFixture):

    @classmethod
    def postSetUpClass(cls):
        trip = cls.trips[0]
        douglas = cls.env.douglas
        cls.comment = cls.env.trips.add_comment(trip['id'], douglas.email,
                'This is a test')
        url = '/trips/%s/comments' % trip['id']
        cls.comment_results = cls.perform_request(url, method="GET")

    def test_get_trip_comments(self):
        '''Comment post response should have owner and comment'''
        expected_response = {
                'id': self.comment['id'],
                'owner': self.env.douglas.email,
                'comment': 'This is a test'
                }
        self.assertDictContainsSubset(expected_response, self.comment_results[0])

if __name__ == '__main__':
    unittest.main()

