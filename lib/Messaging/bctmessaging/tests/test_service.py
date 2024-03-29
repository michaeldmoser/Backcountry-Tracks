import unittest 

import pika
import uuid
import json

from tptesting import fakepika, environment
from bctmessaging.tests.utils import create_messaging_channel, create_endpoint_sut
from bctmessaging.endpoints import MessagingEndPointController

class TestMessagingEndPointController(unittest.TestCase):

    def setUp(self):
        self.service_return = {
                'jsonrpc': '2.0',
                'result': {
                    'some': 'data',
                    'that': 'should be',
                    'returned': 'ya!'
                    },
                }
        class MessageServiceSpy(object):
            def service_method(spy, one, two, three, four, five):
                spy.args = [one, two, three, four, five]
                return self.service_return['result']
        self.spy_service = MessageServiceSpy()

        self.queue_name = 'an_rpc_queue'
        self.reply_exchange = 'rpc_reply_exchange'
        self.rpc_args = [1, 2, 'three', 'four', {'five': 'six'}]
        method_name = 'service_method'

        mq, request, self.properties = create_endpoint_sut(self.spy_service,
                method_name, queue_name=self.queue_name, rpc_args=self.rpc_args,
                reply_exchange_name=self.reply_exchange)
        self.service_return['id'] = self.properties.correlation_id

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
        expected_reply_to = "rpc.reply.%s" % self.properties.reply_to
        self.assertEquals(expected_reply_to, routing_key)

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

        create_endpoint_sut(spy_service, method_name, rpc_args=rpc_args)

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

        create_endpoint_sut(stub_service, method_name, rpc_args=rpc_args)

class TestAcknowlegesMessages(unittest.TestCase):

    def test_acknowledge_on_none(self):
        '''Verify that the message is acknowledged when service returns None'''
        class MessageServiceSpy(object):
            def service_method(spy):
                return None
        spy_service = MessageServiceSpy()

        queue_name = 'an_rpc_queue'
        reply_exchange = 'rpc_reply_exchange'
        method_name = 'service_method'

        mq, request, properties = create_endpoint_sut(spy_service,
                method_name, queue_name=queue_name, rpc_args=[],
                reply_exchange_name=reply_exchange)

        usage = mq.verify_usage(mq._channel.basic_ack, '*',
                {'delivery_tag': 1, 'multiple': False})
        self.assertTrue(usage)

    def test_acknowledge_on_return(self):
        '''Verify that the message is acknowledged when service returns other than None'''
        class MessageServiceSpy(object):
            def service_method(spy):
                return "Hi" 
        spy_service = MessageServiceSpy()

        queue_name = 'an_rpc_queue'
        reply_exchange = 'rpc_reply_exchange'
        method_name = 'service_method'

        mq, request, properties = create_endpoint_sut(spy_service,
                method_name, queue_name=queue_name, rpc_args=[],
                reply_exchange_name=reply_exchange)

        usage = mq.verify_usage(mq._channel.basic_ack, '*',
                {'delivery_tag': 1, 'multiple': False})
        self.assertTrue(usage)

    def test_acknowledge_on_exception(self):
        '''Verify that the message is acknowledged when service raises an exception'''
        class MessageServiceSpy(object):
            def service_method(spy):
                raise ValueError
        spy_service = MessageServiceSpy()

        queue_name = 'an_rpc_queue'
        reply_exchange = 'rpc_reply_exchange'
        method_name = 'service_method'

        mq, request, properties = create_endpoint_sut(spy_service,
                method_name, queue_name=queue_name, rpc_args=[],
                reply_exchange_name=reply_exchange, trigger=False)

        try:
            mq.trigger_consume(queue_name)
        except ValueError:
            pass

        usage = mq.verify_usage(mq._channel.basic_ack, '*',
                {'delivery_tag': 1, 'multiple': False})
        self.assertTrue(usage)

class TestMessagingEndPointControllerExceptions(unittest.TestCase):

    def test_handles_general_exception(self):
        env = environment.create()
        self.service_return = {
                'jsonrpc': '2.0',
                'result': {
                    'some': 'data',
                    'that': 'should be',
                    'returned': 'ya!'
                    },
                }
        class MessageServiceSpy(object):
            def service_method(spy):
                raise Exception('Generic exeption raised in service_method')
        self.spy_service = MessageServiceSpy()

        self.queue_name = 'an_rpc_queue'
        self.reply_exchange = 'rpc_reply_exchange'
        self.rpc_args = []
        method_name = 'service_method'

        mq, request, self.properties = create_endpoint_sut(self.spy_service,
                method_name, queue_name=self.queue_name, rpc_args=self.rpc_args,
                reply_exchange_name=self.reply_exchange)
        self.service_return['id'] = self.properties.correlation_id

        self.reply = mq.published_messages[0]

        jsonrpc_response = json.loads(self.reply.body)
        response_should_be = {
                'jsonrpc': '2.0',
                'id': self.properties.correlation_id,
                'error': {
                    'code': -32000,
                    'message': 'Generic exeption raised in service_method',
                    }
                }

        self.assertEquals(response_should_be, jsonrpc_response)

class TestNoneResponse(unittest.TestCase):

    def test_replies_with_none(self):
        '''Should reply to the RPC with None'''
        class MessageServiceSpy(object):
            def service_method(spy):
                return None
        spy_service = MessageServiceSpy()

        queue_name = 'an_rpc_queue'
        reply_exchange = 'rpc_reply_exchange'
        method_name = 'service_method'

        mq, request, properties = create_endpoint_sut(spy_service,
                method_name, queue_name=queue_name, rpc_args=[],
                reply_exchange_name=reply_exchange)

        reply = mq.published_messages[0]

        expected = {
                'jsonrpc': '2.0',
                'result': None,
                'id': properties.correlation_id
                }

        self.assertEquals(expected, json.loads(reply.body))

    def test_no_reply_without_correlation_id(self):
        '''Should reply to the RPC with None'''
        class MessageServiceSpy(object):
            def service_method(spy):
                return None
        spy_service = MessageServiceSpy()

        queue_name = 'an_rpc_queue'
        reply_exchange = 'rpc_reply_exchange'
        method_name = 'service_method'

        mq, request, properties = create_endpoint_sut(spy_service,
                method_name, queue_name=queue_name, rpc_args=[],
                reply_exchange_name=reply_exchange, correlation_id=None)

        self.assertEquals(len(mq.published_messages), 0)

if __name__ == '__main__':
    unittest.main()


