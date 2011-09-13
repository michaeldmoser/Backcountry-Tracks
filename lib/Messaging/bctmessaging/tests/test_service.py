import unittest 

import pika
import uuid
import json

from tptesting import fakepika
from bctmessaging.tests.utils import create_messaging_channel, create_service_sut
from bctmessaging.services import MessagingServiceController

class TestMessagingServiceController(unittest.TestCase):

    def setUp(self):
        self.service_return = {
                'some': 'data',
                'that': 'should be',
                'returned': 'ya!'
                }
        class MessageServiceSpy(object):
            def service_method(spy, one, two, three, four, five):
                spy.args = [one, two, three, four, five]
                return self.service_return
        self.spy_service = MessageServiceSpy()

        self.queue_name = 'an_rpc_queue'
        self.reply_exchange = 'rpc_reply_exchange'
        self.rpc_args = [1, 2, 'three', 'four', {'five': 'six'}]
        method_name = 'service_method'

        mq, request, self.properties = create_service_sut(self.spy_service,
                method_name, queue_name=self.queue_name, rpc_args=self.rpc_args,
                reply_exchange_name=self.reply_exchange)

        self.reply = mq.published_messages[0]

    def test_reply(self):
        '''Sends the reply message with the correct body'''
        body = json.loads(self.reply.body)
        self.assertEquals(body, self.service_return)

    def test_positional_args(self):
        '''Test the use of positional args'''
        self.assertEquals(self.spy_service.args, self.rpc_args)

    def test_sent_to_exchange(self):
        '''Response message gets sent to rpc_reply exchange'''
        exchange = self.reply.exchange
        self.assertEquals(self.reply_exchange, exchange)

    def test_routing_key(self):
        '''Response sent to correct routing_key'''
        routing_key = self.reply.routing_key
        self.assertEquals(self.properties.reply_to, routing_key)

    def test_content_type(self):
        '''Respone content type is json'''
        content_type = self.reply.properties.content_type
        self.assertEquals('application/json', content_type)

    def test_correlation_id(self):
        '''Response has correct correlation id'''
        correlation_id = self.reply.properties.correlation_id
        self.assertEquals(self.properties.correlation_id, correlation_id)

    def test_delivery_mode(self):
        '''Does not need to be a persisted message'''
        delivery_mode = self.reply.properties.delivery_mode
        self.assertIsNone(delivery_mode)

class TestDictArguments(unittest.TestCase):
    def runTest(self):
        '''Test the usage of dict() arguments'''
        class MessageServiceSpy(object):
            def service_method(spy, arg1=None, arg2=None, arg3=None):
                spy.arg1 = arg1
                spy.arg2 = arg2
                spy.arg3 = arg3
                return {} 

        spy_service = MessageServiceSpy()
        method_name = 'service_method'
        rpc_args = {'arg3': 'three', 'arg1': 'one', 'arg2': 'two'}

        create_service_sut(spy_service, method_name, rpc_args=rpc_args)

        actual_args = {
                'arg1': spy_service.arg1,
                'arg2': spy_service.arg2,
                'arg3': spy_service.arg3,
                }
        self.assertEquals(actual_args, rpc_args)

class TestAlternateMethod(unittest.TestCase):
    def runTest(self):
        '''Test the use of a different method'''
        class MessageServiceStub(object):
            def alternate_method(stub, arg1=None, arg2=None, arg3=None):
                return {} 

        stub_service = MessageServiceStub()
        queue_name = 'an_rpc_queue'
        rpc_args = {'arg3': 'three', 'arg1': 'one', 'arg2': 'two'}
        method_name = "alternate_method"

        create_service_sut(stub_service, method_name, rpc_args=rpc_args)

if __name__ == '__main__':
    unittest.main()


