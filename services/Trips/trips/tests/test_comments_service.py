import unittest

from copy import deepcopy

from uuid import uuid4
import json
from datetime import datetime

from tptesting import environment

from trips.tests import utils

from trips.service import TripsDb
from tptesting.fakeriak import RiakClientFake, RiakBinary
from tptesting.fakepika import SelectConnectionFake
from bctmessaging.remoting import RemotingClient

class TestTripComment(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()
        self.riak = RiakClientFake()
        self.bucket_name = 'trips'
        self.bucket = self.riak.bucket(self.bucket_name)

        pika_connection = SelectConnectionFake()
        channel = pika_connection._channel
        rpc_client = RemotingClient(channel)

        self.app = TripsDb(
                rpc_client,
                self.riak, 
                self.bucket_name, 
                'http://test.com',
                )


        self.trip_id = unicode(uuid4())

        ramona = self.environ.ramona
        self.trip = {
            'name': 'Glacier',
            'start': '2012-07-19',
            'end': '2012-07-24',
            'destination': 'Glacier National Park',
            'friends': [
                {'first': ramona.first_name,
                    'last': ramona.last_name,
                    'email': ramona.email,
                    'invite_status': 'accepted'}
                ],
            'gear': dict(),
            'groupgear': list()
            }
        self.bucket.add_document(self.trip_id, self.trip)

        adventurers = self.riak.bucket('adventurers')
        adventurers.add_document(ramona.email, ramona)

    def test_add_a_comment(self):
        '''Add a comment to a trip'''
        self.app.comment(self.trip_id, self.environ.ramona.email,
                'This is a test comment')

        trip = self.bucket.get(str(self.trip_id))
        links = trip.get_links()
        comments = filter(lambda x: x.get_tag() == 'comment', links)

        comment = comments[0].get().get_data()
        expected_comment = {
                'comment': 'This is a test comment',
                'date': str(datetime.utcnow().strftime('%B %d, %Y %H:%M:%S GMT+0000')),
                'owner': self.environ.ramona.email,
                'first_name': self.environ.ramona.first_name,
                'last_name': self.environ.ramona.last_name,
                }

        self.assertDictContainsSubset(expected_comment, comment)

    def test_in_comments_bucket(self):
        '''Comment should be in the trips buckets'''
        self.app.comment(self.trip_id, self.environ.ramona.email,
                'This is a test comment')
        trip = self.bucket.get(str(self.trip_id))
        links = trip.get_links()
        comments = filter(lambda x: x.get_tag() == 'comment', links)

        self.assertEquals(comments[0]._bucket, 'trips')

    def test_object_has_id(self):
        '''The returned comment should have an id'''
        result = self.app.comment(self.trip_id, self.environ.ramona.email,
                'This is a test comment')

        comments = self.riak.bucket('trips')
        comment = comments.get(str(result['id']))
        self.assertTrue(comment.exists())

    def test_comment_object_returned(self):
        '''Comment should return the stored comment object'''
        result = self.app.comment(self.trip_id, self.environ.ramona.email,
                'This is a test comment')
        expected_comment = {
                'comment': 'This is a test comment',
                'date': str(datetime.utcnow().strftime('%B %d, %Y %H:%M:%S GMT+0000')),
                'owner': self.environ.ramona.email
                }
        self.assertDictContainsSubset(expected_comment, result)

    def test_comment_object_metadata(self):
        '''Comment should have it's object_type metadata set'''
        result = self.app.comment(self.trip_id, self.environ.ramona.email,
                'This is a test comment')
        comments = self.riak.bucket('trips')
        comment = comments.get(str(result['id']))
        
        usermeta = comment.get_usermeta()
        
        self.assertDictContainsSubset({'object_type': 'comment'}, usermeta)

class TestRetrieveComments(utils.TestTripFixture):

    def continueSetUp(self):
        adventurers = self.riak.bucket('adventurers')
        adventurers.add_document(self.environ.ramona.email, self.environ.ramona)

        result = self.app.comment(self.trip_id, self.environ.ramona.email,
                'This is a test comment')
        result = self.app.comment(self.trip_id, self.environ.ramona.email,
                'This is a test comment 2')

    def test_get_comments(self):
        '''Should return comments from database'''
        comments = self.app.get_comments(self.trip_id)
        comment_texts = [comment['comment'] for comment in comments]

        expected_comments = ['This is a test comment', 'This is a test comment 2']
        self.assertEquals(expected_comments, comment_texts)

class TestSendCommentNotificationEmail(utils.TestTripFixture):

    def continueSetUp(self):
        adventurers = self.riak.bucket('adventurers')
        adventurers.add_document(self.environ.ramona.email, self.environ.ramona)

        result = self.app.comment(self.trip_id, self.environ.ramona.email,
                'This is a test comment')

        self.message = self.channel.messages[0]
        self.jsonrpc = json.loads(self.message.body)

    def test_douglas_should_receive_email(self):
        '''Douglas should have been sent a discussion email notification'''
        to = self.jsonrpc['params']['to'];
        self.assertIn(self.environ.douglas.email, to)

    def test_ramona_should_receive_email(self):
        '''Ramona should have been sent a discussion email notification'''
        to = self.jsonrpc['params']['to'];
        self.assertIn(self.environ.ramona.email, to)

    def test_albert_should_not_receive_email(self):
        '''Albert should not have been sent a discussion email notification'''
        to = self.jsonrpc['params']['to'];
        self.assertNotIn(self.environ.albert.email, to)
        

if __name__ == '__main__':
    unittest.main()

