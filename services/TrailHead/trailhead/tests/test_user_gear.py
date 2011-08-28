import unittest

import json
import pika

from tptesting import faketornado, environment, fakepika

from trailhead.tests.utils import create_fake_application, setup_handler
from trailhead.gear import UserGearListHandler


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

    def test_gear_exchange_used(self):
        '''Should send the message via the gear exchange'''
        exchange = self.sent_message.exchange
        self.assertEquals('gear', exchange)

    def test_routing_key(self):
        '''Should use the gear.user.rpc routing key'''
        routing_key = self.sent_message.routing_key
        self.assertEquals('gear.user.rpc', routing_key)

    def test_content_type(self):
        '''Should use application/json-rpc content-type'''
        content_type = self.sent_message.properties.content_type
        self.assertEquals('application/json-rpc', content_type)
        
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

    def test_reply_to(self):
        '''The reply_to should route back to the TrailHead service'''
        reply_to = self.sent_message.properties.reply_to
        self.assertEquals(self.application.mq.rpc_reply, reply_to)

class TestUserGearListReply(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()
        url = '/app/users/' + self.environ.douglas.email + '/gear'
        self.handler, self.application, self.pika = setup_handler(UserGearListHandler,
                'GET', url, user=self.environ.douglas.email)
        self.request = self.handler.request

        self.handler.get(self.environ.douglas.email)
        self.sent_message = self.pika.published_messages[0]

        self.headers = pika.BasicProperties(
                correlation_id = self.sent_message.properties.correlation_id,
                content_type = 'application/json'
                )

        self.gear_list = [
                {'name': 'Backpack', 'description': 'A backpack', 'weight': '48'},
                {'name': 'Stove', 'description': 'A stove', 'weight': '10'},
                {'name': 'Sleeping bag', 'description': 'A sleeping bag', 'weight': '38'},
                ]

        reply_queue = self.application.mq.rpc_reply

        self.pika.inject(reply_queue, self.headers, json.dumps(self.gear_list))
        self.pika.trigger_consume(reply_queue)

    def test_gear_list_response(self):
        '''Should return a list of gear for the user'''
        headers, body = self.request._output.split('\r\n\r\n')
        actual_gear_list = json.loads(body)
        self.assertEquals(self.gear_list, actual_gear_list)

    def test_response_status(self):
        '''Should respond with a 200 HTTP status'''
        self.assertEquals(self.handler._status_code, 200)

    def test_finishes_request(self):
        '''Reports being finished to tornado'''
        self.assertTrue(self.request.was_called(self.request.finish))

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

        self.rpc_response = self.pieceofgear.copy()
        self.rpc_response.update({'id': '1234', 'owner': self.adventurer.email})

        reply_queue = self.application.mq.rpc_reply

        self.pika.inject(reply_queue, self.headers, json.dumps(self.rpc_response))
        self.pika.trigger_consume(reply_queue)

    def test_rpc_response(self):
        '''Should return a list of gear for the user'''
        headers, body = self.request._output.split('\r\n\r\n')
        actual_response = json.loads(body)
        self.assertEquals(self.rpc_response, actual_response)

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

    def test_gear_exchange_used(self):
        '''Should send the message via the gear exchange'''
        exchange = self.sent_message.exchange
        self.assertEquals('gear', exchange)

    def test_routing_key(self):
        '''Should use the gear.user.rpc routing key'''
        routing_key = self.sent_message.routing_key
        self.assertEquals('gear.user.rpc', routing_key)

    def test_content_type(self):
        '''Should use application/json-rpc content-type'''
        content_type = self.sent_message.properties.content_type
        self.assertEquals('application/json-rpc', content_type)
        
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

    def test_reply_to(self):
        '''The reply_to should route back to the TrailHead service'''
        reply_to = self.sent_message.properties.reply_to
        self.assertEquals(self.application.mq.rpc_reply, reply_to)




if __name__ == '__main__':
    unittest.main()

