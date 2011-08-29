import pdb
import unittest

import json
import pika

from tptesting import faketornado, environment, fakepika

from trailhead.tests.utils import create_fake_application
from trailhead.gear import UserGearListHandler


class TestUserGearListSendRPC(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()
        self.application, self.pika = create_fake_application()

        self.request = faketornado.HTTPRequestFake(
                'get',
                '/app/users/' + self.environ.douglas.email + '/gear',
                )
        self.handler = UserGearListHandler(self.application, self.request)
        self.handler._transforms = []
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
        self.application, self.pika = create_fake_application()

        self.request = faketornado.HTTPRequestFake(
                'get',
                '/app/users/' + self.environ.douglas.email + '/gear',
                )
        self.handler = UserGearListHandler(self.application, self.request)
        self.handler._transforms = []
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



if __name__ == '__main__':
    unittest.main()

