import unittest

import json
import pika
import uuid

from tptesting import faketornado, environment, fakepika, thandlers

from trailhead.tests.utils import create_fake_application, setup_handler

from trips.friends import FriendsHandler

class TestInviteFriend(thandlers.TornadoHandlerTestCase):

    def handler_setup(self):
        self.trip_id = str(uuid.uuid4())
        self.invite = {
            'email': self.environ.douglas.email,
            'first': self.environ.douglas.first_name,
            'last': self.environ.douglas.last_name,
            'invite_status': 'invited'
            }

    def request_handler(self):
        return FriendsHandler

    def url(self):
        return '/app/trips/' + self.trip_id + '/friends'

    def active_user(self):
        return self.environ.ramona.email

    def method(self):
        return 'POST'

    def method_args(self):
        return list([self.trip_id]), dict()

    def rpc_result(self):
        invite_response = self.invite.copy()
        invite_response.update({'id': '1234'})
        return invite_response

    def http_response(self):
        return self.rpc_result()

    def expected_rpc_request(self):
        return 'invite', [self.trip_id, self.environ.ramona.email, self.invite]

    def expected_durability(self):
        return True

    def remote_service_name(self):
        return 'Trips'

    def http_request_body(self):
        return json.dumps(self.invite)

class TestAcceptInvite(thandlers.TornadoHandlerTestCase):

    def handler_setup(self):
        self.trip_id = str(uuid.uuid4())
        self.invite_response = {
            'email': self.environ.douglas.email,
            'first': self.environ.douglas.first_name,
            'last': self.environ.douglas.last_name,
            'invite_status': 'accepted'
            }

        self.invite_update =  {
            'invite_status': 'accepted'
            }

    def request_handler(self):
        return FriendsHandler

    def url(self):
        return '/app/trips/' + self.trip_id + '/friends/' + self.invite_response['email']

    def active_user(self):
        return self.environ.douglas.email

    def method(self):
        return 'PUT'

    def method_args(self):
        return list([self.trip_id, self.environ.douglas.email]), dict()

    def rpc_result(self):
        return self.invite_response

    def http_response(self):
        return self.rpc_result()

    def expected_rpc_request(self):
        return 'accept', [self.trip_id, self.environ.douglas.email]

    def expected_durability(self):
        return True

    def remote_service_name(self):
        return 'Trips'

    def http_request_body(self):
        return json.dumps(self.invite_update)

if __name__ == '__main__':
    unittest.main()

