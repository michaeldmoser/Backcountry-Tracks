import unittest

import json
import pika
import uuid

from tptesting import faketornado, environment, fakepika, thandlers
from trailhead.tests.utils import create_fake_application, setup_handler

from gear.handlers import UserGearListHandler

class TestUserGearDelete(unittest.TestCase):
    '''
    Tests the process of receiving a DELETE on /users/<user@email.com>/gear/<id>
    and sending a delete json rpc request
    '''

    def setUp(self):
        self.environ = environment.create()
        self.adventurer = self.environ.douglas

        self.gear_id = str(uuid.uuid4())
        url = '/app/users/%s/gear/%s' % (self.adventurer.email, self.gear_id)
        self.handler, self.application, self.pika = setup_handler(UserGearListHandler,
                'DELETE', url, user=self.adventurer.email)
        self.request = self.handler.request

        self.handler.delete(self.adventurer.email, self.gear_id)

        self.sent_message = self.pika.published_messages[0]

    def test_rpc_response(self):
        '''Should return a list of gear for the user'''
        self.handler.finish() # Tornado does this automatically for non-async methods
        headers, body = self.request._output.split('\r\n\r\n')
        self.assertEquals('', body)

    def test_response_status(self):
        '''Should respond with a 204 HTTP status'''
        self.assertEquals(self.handler._status_code, 204)

    def test_send_create_request_body(self):
        '''Sends a JSON-RPC message request for creating a piece of gear'''
        sent_request = json.loads(self.sent_message.body)
        del sent_request['id'] # we don't care about the id in this context

        expected_request = {
                'jsonrpc': '2.0',
                'method': 'delete',
                'params': [self.adventurer.email, self.gear_id],
                }
        self.assertEquals(expected_request, sent_request)

    def test_delivery_mode(self):
        '''Does not need to be a persisted message'''
        delivery_mode = self.sent_message.properties.delivery_mode
        self.assertIsNone(delivery_mode)

class TestUserGearList(thandlers.TornadoHandlerTestCase):

    adventurer = str(uuid.uuid4())

    GEAR_LIST = [
                {'name': 'Backpack', 'description': 'A backpack', 'weight': '48'},
                {'name': 'Stove', 'description': 'A stove', 'weight': '10'},
                {'name': 'Sleeping bag', 'description': 'A sleeping bag', 'weight': '38'},
                ]

    def request_handler(self):
        return UserGearListHandler

    def url(self):
        return '/app/gear'

    def active_user(self):
        return self.adventurer

    def method(self):
        return 'GET'

    def method_args(self):
        return [], {}

    def rpc_result(self):
        return TestUserGearList.GEAR_LIST

    def http_response(self):
        return TestUserGearList.GEAR_LIST

    def expected_rpc_request(self):
        return 'list', [self.adventurer]

    def expected_durability(self):
        return False

    def remote_service_name(self):
        return 'Gear'

class TestUserGearCreate(thandlers.TornadoHandlerTestCase):

    adventurer = str(uuid.uuid4())
    key = str(uuid.uuid4())

    GEAR = {'name': 'Backpack', 'description': 'A backpack', 'weight': '48'}

    def request_handler(self):
        return UserGearListHandler

    def url(self):
        return '/app/gear'

    def active_user(self):
        return self.adventurer

    def method(self):
        return 'POST'

    def method_args(self):
        return [], {}

    def rpc_result(self):
        gear = TestUserGearCreate.GEAR.copy()
        gear['id'] = self.key
        return gear

    def http_response(self):
        return self.rpc_result()

    def http_request_body(self):
        return json.dumps(self.GEAR)

    def expected_rpc_request(self):
        return 'create', [self.adventurer, self.GEAR]

    def expected_durability(self):
        return False

    def remote_service_name(self):
        return 'Gear'

class TestUserGearUpdate(thandlers.TornadoHandlerTestCase):

    adventurer = str(uuid.uuid4())
    key = str(uuid.uuid4())

    GEAR = {'id': key, 'name': 'Backpack', 'description': 'A backpack', 'weight': '48'}

    def request_handler(self):
        return UserGearListHandler

    def url(self):
        return '/app/gear/' + self.key

    def active_user(self):
        return self.adventurer

    def method(self):
        return 'PUT'

    def method_args(self):
        return [self.key], {}

    def rpc_result(self):
        gear = TestUserGearCreate.GEAR.copy()
        gear['id'] = self.key
        return gear

    def http_response(self):
        return self.rpc_result()

    def http_request_body(self):
        return json.dumps(self.GEAR)

    def expected_rpc_request(self):
        return 'update', [self.adventurer, self.key, self.GEAR]

    def expected_durability(self):
        return False

    def remote_service_name(self):
        return 'Gear'

if __name__ == '__main__':
    unittest.main()

