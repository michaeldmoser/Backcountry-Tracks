import unittest

import json
import pika
import uuid

from tptesting import faketornado, environment, fakepika, thandlers

from trailhead.tests.utils import create_fake_application, setup_handler

from trips.group_gear_handler import GroupGearHandler

class TestPersonalGearHandler(thandlers.TornadoHandlerTestCase):

    def handler_setup(self):
        self.trip_id = str(uuid.uuid4())

    def request_handler(self):
        return GroupGearHandler

    def url(self):
        return '/app/trips/' + self.trip_id + '/gear/group'

    def active_user(self):
        return self.environ.ramona.email

    def method(self):
        return 'GET'

    def method_args(self):
        return list([self.trip_id]), dict()

    def rpc_result(self):
        gear = self.environ.data['gear']
        
        def set_gear_owner(item):
            gear_item = item.copy()
            gear_item['owner'] = self.active_user()

            return gear_item
        trip_gear = map(set_gear_owner, gear)
        
        return trip_gear

    def http_response(self):
        return self.rpc_result()

    def expected_rpc_request(self):
        return 'get_group_gear', [self.trip_id]

    def expected_durability(self):
        return False

    def remote_service_name(self):
        return 'Trips'

class TestGroupGearHandlerPUT(thandlers.TornadoHandlerTestCase):

    def handler_setup(self):
        self.trip_id = str(uuid.uuid4())
        self.gear_id = str(uuid.uuid4())
        self.gear = self.environ.data['gear'][0].copy()
        self.gear['id'] = self.gear_id

    def request_handler(self):
        return GroupGearHandler

    def url(self):
        return '/app/trips/' + self.trip_id + '/gear/group/' + self.gear_id

    def active_user(self):
        return self.environ.ramona.email

    def method(self):
        return 'PUT'

    def method_args(self):
        return list([self.trip_id, self.gear_id]), dict()

    def http_request_body(self):
        return json.dumps(self.gear)

    def rpc_result(self):
        return self.gear

    def http_response(self):
        return self.rpc_result()

    def expected_rpc_request(self):
        return 'share_gear', [self.trip_id, self.gear]

    def expected_durability(self):
        return True

    def remote_service_name(self):
        return 'Trips'

class TestGroupGearHandlerDELETE(thandlers.TornadoHandlerTestCase):

    def handler_setup(self):
        self.trip_id = str(uuid.uuid4())
        self.gear_id = str(uuid.uuid4())
        self.gear = self.environ.data['gear'][0].copy()
        self.gear['id'] = self.gear_id

    def request_handler(self):
        return GroupGearHandler

    def url(self):
        return '/app/trips/' + self.trip_id + '/gear/group/' + self.gear_id

    def active_user(self):
        return self.environ.ramona.email

    def method(self):
        return 'DELETE'

    def method_args(self):
        return list([self.trip_id, self.gear_id]), dict()

    def http_request_body(self):
        return ''

    def rpc_result(self):
        return ''

    def http_response(self):
        return ''

    def expected_rpc_request(self):
        return 'unshare_gear', [self.trip_id, self.gear_id]

    def expected_durability(self):
        return True

    def remote_service_name(self):
        return 'Trips'

if __name__ == '__main__':
    unittest.main()

