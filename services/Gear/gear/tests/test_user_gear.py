import unittest

import json
import pika
import uuid

from tptesting import faketornado, environment, fakepika, thandlers
from trailhead.tests.utils import create_fake_application, setup_handler

from gear.handlers import UserGearListHandler


class TestUserGearListSendRPC(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()

        url = '/app/users/' + self.environ.douglas.email + '/gear'
        self.handler, self.application, self.pika = setup_handler(UserGearListHandler,
                'GET', url, user=self.environ.douglas.email)

        self.handler.get(self.environ.douglas.email)
        self.sent_message = self.pika.published_messages[0]

    def test_send_request_for_gear_body(self):
        '''Sends a JSON-RPC message request for listing gear'''
        sent_request = json.loads(self.sent_message.body)
        del sent_request['id'] # we don't care about the id in this context

        expected_request = {
                'jsonrpc': '2.0',
                'method': 'list',
                'params': [self.environ.douglas.email],
                }
        self.assertEquals(expected_request, sent_request)

    def test_delivery_mode(self):
        '''Does not need to be a persisted message'''
        delivery_mode = self.sent_message.properties.delivery_mode
        self.assertIsNone(delivery_mode)

    def test_correlation_id_jsonrpc_id(self):
        '''The messages correlation_id and the json-rpc id should be the same'''
        sent_request = json.loads(self.sent_message.body)
        json_id = sent_request['id']
        correlation_id = self.sent_message.properties.correlation_id

        self.assertEquals(json_id, correlation_id)

class TestUserGearCreate(unittest.TestCase):
    '''
    Tests the process of receiving a POST on /users/<user@email.com>/gear
    and sending a create json rpc request
    '''

    def setUp(self):
        self.environ = environment.create()
        self.adventurer = self.environ.douglas

        self.pieceofgear = {
                'name': 'Backpack',
                'description': 'A backpack',
                'weight': '48'
                }
        request_body = json.dumps(self.pieceofgear)
        headers = {'Content-Type': 'application/json'}

        url = '/app/users/%s/gear' % self.adventurer.email
        self.handler, self.application, self.pika = setup_handler(UserGearListHandler,
                'POST', url, user=self.adventurer.email, body=request_body,
                headers=headers)
        self.request = self.handler.request

        self.handler.post(self.adventurer.email)

        self.sent_message = self.pika.published_messages[0]

        self.headers = pika.BasicProperties(
                correlation_id = self.sent_message.properties.correlation_id,
                content_type = 'application/json'
                )

        self.rpc_response = {
                'jsonrpc': '2.0',
                'result': self.pieceofgear.copy(),
                'id': self.sent_message.properties.correlation_id,
                }
        self.rpc_response.update({'id': '1234', 'owner': self.adventurer.email})

        reply_queue = self.application.mq.remoting.queue

        self.pika.inject(reply_queue, self.headers, json.dumps(self.rpc_response))
        self.pika.trigger_consume(reply_queue)

    def test_rpc_response(self):
        '''Should return a list of gear for the user'''
        headers, body = self.request._output.split('\r\n\r\n')
        actual_response = json.loads(body)
        self.assertEquals(self.rpc_response['result'], actual_response)

    def test_response_status(self):
        '''Should respond with a 200 HTTP status'''
        self.assertEquals(self.handler._status_code, 200)

    def test_finishes_request(self):
        '''Reports being finished to tornado'''
        self.assertTrue(self.request.was_called(self.request.finish))

    def test_send_create_request_body(self):
        '''Sends a JSON-RPC message request for creating a piece of gear'''
        sent_request = json.loads(self.sent_message.body)
        del sent_request['id'] # we don't care about the id in this context

        expected_request = {
                'jsonrpc': '2.0',
                'method': 'create',
                'params': [self.adventurer.email, self.pieceofgear]
                }
        self.assertEquals(expected_request, sent_request)

    def test_delivery_mode(self):
        '''Does not need to be a persisted message'''
        delivery_mode = self.sent_message.properties.delivery_mode
        self.assertIsNone(delivery_mode)

    def test_correlation_id_jsonrpc_id(self):
        '''The messages correlation_id and the json-rpc id should be the same'''
        sent_request = json.loads(self.sent_message.body)
        json_id = sent_request['id']
        correlation_id = self.sent_message.properties.correlation_id

        self.assertEquals(json_id, correlation_id)

class TestUserGearUpdate(unittest.TestCase):
    '''
    Tests the process of receiving a PUT on /users/<user@email.com>/gear/<id>
    and sending a update json rpc request
    '''

    def setUp(self):
        self.environ = environment.create()
        self.adventurer = self.environ.douglas

        self.gear_id = str(uuid.uuid4())
        self.pieceofgear = {
                'name': 'Backpack',
                'description': 'A backpack',
                'weight': '48',
                'owner': self.adventurer.email,
                'id': self.gear_id,
                }
        request_body = json.dumps(self.pieceofgear)
        headers = {'Content-Type': 'application/json'}

        url = '/app/users/%s/gear' % self.adventurer.email
        self.handler, self.application, self.pika = setup_handler(UserGearListHandler,
                'PUT', url, user=self.adventurer.email, body=request_body,
                headers=headers)
        self.request = self.handler.request

        self.handler.put(self.adventurer.email, self.pieceofgear['id'])

        self.sent_message = self.pika.published_messages[0]

        self.rpc_response = {
                'jsonrpc': '2.0',
                'result': self.pieceofgear,
                'id': self.sent_message.properties.correlation_id,
                }

        self.headers = pika.BasicProperties(
                correlation_id = self.sent_message.properties.correlation_id,
                content_type = 'application/json'
                )

        reply_queue = self.application.mq.remoting.queue

        self.pika.inject(reply_queue, self.headers, json.dumps(self.rpc_response))
        self.pika.trigger_consume(reply_queue)

    def test_rpc_response(self):
        '''Should return a list of gear for the user'''
        headers, body = self.request._output.split('\r\n\r\n')
        actual_response = json.loads(body)
        self.assertEquals(self.rpc_response['result'], actual_response)

    def test_response_status(self):
        '''Should respond with a 200 HTTP status'''
        self.assertEquals(self.handler._status_code, 200)

    def test_finishes_request(self):
        '''Reports being finished to tornado'''
        self.assertTrue(self.request.was_called(self.request.finish))

    def test_send_create_request_body(self):
        '''Sends a JSON-RPC message request for creating a piece of gear'''
        sent_request = json.loads(self.sent_message.body)
        del sent_request['id'] # we don't care about the id in this context

        expected_request = {
                'jsonrpc': '2.0',
                'method': 'update',
                'params': [self.adventurer.email, self.gear_id, self.pieceofgear]
                }
        self.assertEquals(expected_request, sent_request)

    def test_delivery_mode(self):
        '''Does not need to be a persisted message'''
        delivery_mode = self.sent_message.properties.delivery_mode
        self.assertIsNone(delivery_mode)

    def test_correlation_id_jsonrpc_id(self):
        '''The messages correlation_id and the json-rpc id should be the same'''
        sent_request = json.loads(self.sent_message.body)
        json_id = sent_request['id']
        correlation_id = self.sent_message.properties.correlation_id

        self.assertEquals(json_id, correlation_id)

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

class TestUserGearListReply(thandlers.TornadoHandlerTestCase):

    GEAR_LIST = [
                {'name': 'Backpack', 'description': 'A backpack', 'weight': '48'},
                {'name': 'Stove', 'description': 'A stove', 'weight': '10'},
                {'name': 'Sleeping bag', 'description': 'A sleeping bag', 'weight': '38'},
                ]

    def request_handler(self):
        return UserGearListHandler

    def url(self):
        return '/app/users/' + self.environ.douglas.email + '/gear'

    def active_user(self):
        return self.environ.douglas.email

    def method(self):
        return 'GET'

    def method_args(self):
        return [self.environ.douglas.email], {}

    def rpc_result(self):
        return TestUserGearListReply.GEAR_LIST

    def http_response(self):
        return TestUserGearListReply.GEAR_LIST

    def expected_rpc_request(self):
        return 'list', [self.environ.douglas.email]

    def expected_durability(self):
        return False

    def remote_service_name(self):
        return 'Gear'

if __name__ == '__main__':
    unittest.main()

