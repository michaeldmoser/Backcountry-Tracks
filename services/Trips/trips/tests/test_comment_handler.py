import unittest

import json
import pika
import uuid
from datetime import datetime

from tptesting import thandlers

from trips.comments_handler import CommentsHandler

class TestRouteHandlerPOST(thandlers.TornadoHandlerTestCase):

    def handler_setup(self):
        self.trip_id = str(uuid.uuid4())
        self.comment = 'This is a test comment'
        self.result = {
                'id': str(uuid.uuid4()),
                'date': str(datetime.utcnow().strftime('%B %d, %Y %H:%M:%S GMT+0000')),
                'comment': self.comment,
                'owner': self.active_user()
                }


    def request_handler(self):
        return CommentsHandler

    def url(self):
        return '/app/trips/' + self.trip_id + '/comments'

    def active_user(self):
        return self.environ.ramona.email

    def method(self):
        return 'POST'

    def method_args(self):
        return list([self.trip_id]), dict()

    def rpc_result(self):
        return self.result

    def http_request_body(self):
        return json.dumps({'comment': self.comment})

    def http_response(self):
        return self.rpc_result()

    def expected_rpc_request(self):
        return 'comment', [self.trip_id, self.active_user(), self.comment]

    def expected_durability(self):
        return True

    def remote_service_name(self):
        return 'Trips'

class TestRouteHandlerGET(thandlers.TornadoHandlerTestCase):

    def handler_setup(self):
        self.trip_id = str(uuid.uuid4())
        self.comment = 'This is a test comment'
        self.result = [{
                'id': str(uuid.uuid4()),
                'date': str(datetime.utcnow().strftime('%B %d, %Y %H:%M:%S GMT+0000')),
                'comment': self.comment,
                'owner': self.active_user()
                }]


    def request_handler(self):
        return CommentsHandler

    def url(self):
        return '/app/trips/' + self.trip_id + '/comments'

    def active_user(self):
        return self.environ.ramona.email

    def method(self):
        return 'GET'

    def method_args(self):
        return list([self.trip_id]), dict()

    def rpc_result(self):
        return self.result

    def http_response(self):
        return self.rpc_result()

    def expected_rpc_request(self):
        return 'get_comments', [self.trip_id]

    def expected_durability(self):
        return False

    def remote_service_name(self):
        return 'Trips'

if __name__ == '__main__':
    unittest.main()

