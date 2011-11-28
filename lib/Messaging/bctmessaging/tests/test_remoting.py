import unittest
import uuid
import pika
import json

from tptesting import fakepika

from bctmessaging.remoting import RemoteService, CommandMessage, RemotingClient

class TestCommandMessageBody(unittest.TestCase):

    def test_jsonrpc_message_body(self):
        '''CommandMessage generates a proper JSON-RPrrrrrsage body'''
        message = CommandMessage(method='echo', args=['hello world'])
        jsonrpc = message.body()

        expected_rpc = {
                'jsonrpc': '2.0',
                'method': 'echo', 
                'params': ['hello world'],
                'id': message.message_id
                }

        self.assertEquals(jsonrpc, expected_rpc)

    def test_message_body_args(self):
        '''CommandMessage generates a proper JSON-RPC message body with multiple args'''
        message = CommandMessage(method='echo', args=['hello', 'world'])
        jsonrpc = message.body()

        expected_rpc = {
                'jsonrpc': '2.0',
                'method': 'echo', 
                'params': ['hello', 'world'],
                'id': message.message_id
                }

        self.assertEquals(jsonrpc, expected_rpc)

    def test_message_body_kwargs(self):
        '''CommandMessage generates a proper JSON-RPC message body with kwargs args'''
        kwargs = {'hello': 'world', 'no': 'hi'}
        message = CommandMessage(method='echo', args=kwargs)
        jsonrpc = message.body()

        expected_rpc = {
                'jsonrpc': '2.0',
                'method': 'echo', 
                'params': kwargs,
                'id': message.message_id
                }

        self.assertEquals(jsonrpc, expected_rpc)

    def test_no_args_or_kwargs(self):
        '''CommandMessage generates a proper JSON-RPC message body with no args'''
        message = CommandMessage(method='echo')
        jsonrpc = message.body()

        expected_rpc = {
                'jsonrpc': '2.0',
                'method': 'echo', 
                'id': message.message_id
                }

        self.assertEquals(jsonrpc, expected_rpc)

    def test_not_a_dict_or_list(self):
        '''CommandMessage should raise ValueError is args is not a list(), tuple(), or dict()'''
        with self.assertRaises(ValueError):
            CommandMessage(method='echo', args='not one of the three')

class TestCommandMessageService(unittest.TestCase):
    
    def test_service_name(self):
        '''Set the service name on a command message'''
        command = CommandMessage(method='asdf', service='RandomService')
        self.assertEquals(command.service, 'RandomService')

    def test_default_service_name(self):
        '''Service name should default to remote'''
        command = CommandMessage(method='asdf')
        self.assertEquals(command.service, 'remote')

    def test_default_exchange(self):
        '''Exchange attribute should be None by default'''
        command = CommandMessage(method='asdf')
        self.assertIsNone(command.exchange)

    def test_override_exchange(self):
        '''Can set the exchange via instantiation'''
        command = CommandMessage(method='asdf', exchange='blah')
        self.assertEquals('blah', command.exchange)

    def test_default_persistance(self):
        '''persistant should default to False'''
        command = CommandMessage(method='asdf')
        self.assertFalse(command.persistant)

    def test_content_type(self):
        '''Content type of command message should be application/json'''
        command = CommandMessage(method='asdf')
        self.assertEquals(command.content_type, 'application/json-rpc')

class TestRemoteService(unittest.TestCase):

    def setUp(self):
        self.service_name = 'Echo'
        self.method_name = str(uuid.uuid4()).replace('-', '')
        self.service = RemoteService(self.service_name)
        self.method = getattr(self.service, self.method_name)

    def test_method_with_args(self):
        '''Service should produce CommandMessage when called with *args'''
        command_message = self.method('a', 'b', 'c')

        expected_command = CommandMessage(method=self.method_name, args=['a', 'b', 'c'])

        # the message_id is random set to a know value for comparison
        command_message.message_id = 1
        expected_command.message_id = 1

        self.assertEquals(command_message, expected_command)

    def test_method_with_kwargs(self):
        '''Service should produce CommandMessage when called with **kwargs'''
        kwargs = {'a': 'b', 'c': 'd'}
        command_message = self.method(**kwargs)

        expected_command = CommandMessage(method=self.method_name, args=kwargs)

        # the message_id is random set to a know value for comparison
        command_message.message_id = 1
        expected_command.message_id = 1

        self.assertEquals(command_message, expected_command)

    def test_should_not_support_both(self):
        '''Raise ValueError if both *args and **kwargs are used'''
        with self.assertRaises(ValueError):
            self.method(1, 2, 3, a='b', c='d', e='f')

    def test_service_name(self):
        '''Service name should be set'''
        command = self.method('asdf')
        self.assertEquals(command.service, self.service_name)

class TestRemotingClientMessageSending(unittest.TestCase):

    def setUp(self):
        self.default_exchange = 'adventurer'
        self.pika = fakepika.SelectConnectionFake()
        self.remoting = RemotingClient(channel=self.pika._channel, exchange=self.default_exchange)

        self.service_name = 'Adventurer'
        self.service = self.remoting.remote_service(self.service_name)
        self.command = self.service.login('bob@smith.com', 'secret')


    def test_sends_message_via_default_exchange(self):
        '''Sends a message to the specified default exchange'''
        self.remoting.call(self.command)

        message = self.pika.published_messages[0]
        self.assertEquals(message.exchange, self.default_exchange)

    def test_command_overrides_exchange(self):
        '''Send a message to the exchange specified in the command'''
        self.command.exchange = 'user_logins'
        self.remoting.call(self.command)

        message = self.pika.published_messages[0]
        self.assertEquals(message.exchange, 'user_logins')

    def test_message_persistance(self):
        '''Message should be persistant if command says so'''
        self.command.persistant = True
        self.remoting.call(self.command)

        message = self.pika.published_messages[0]
        self.assertEquals(message.properties.delivery_mode, 2)

    def test_message_not_persistant(self):
        '''Message should not be persistant if command does not specify it'''
        self.command.persistant = False 
        self.remoting.call(self.command)

        message = self.pika.published_messages[0]
        self.assertEquals(message.properties.delivery_mode, None)

    def test_message_content_type(self):
        '''Content-Type should be as command specifies'''
        self.remoting.call(self.command)

        message = self.pika.published_messages[0]
        self.assertEquals(message.properties.content_type, self.command.content_type)

    def test_correlation_id(self):
        '''Messages correlation id should be None (no callback)'''
        self.remoting.call(self.command)

        message = self.pika.published_messages[0]
        self.assertEquals(message.properties.correlation_id, None)


    def test_correlation_id_with_callback(self):
        '''Messages correlation id should be the same as the CommandMessages message_id'''
        def donothing(respone):
            pass

        self.remoting.call(self.command, callback=donothing)

        message = self.pika.published_messages[0]
        self.assertEquals(message.properties.correlation_id, self.command.message_id)

    def test_reply_to(self):
        '''Reply to channel should be the opened channel'''
        self.remoting.call(self.command)

        message = self.pika.published_messages[0]
        reply_to_queue = self.pika._channel.queues.keys()[0]
        self.assertEquals(message.properties.reply_to, reply_to_queue)

    def test_message_body(self):
        '''Test message body encoded as json text'''
        self.remoting.call(self.command)

        message = self.pika.published_messages[0]
        expected_message = self.command.body()
        actual_message = json.loads(message.body)
        self.assertEquals(expected_message, actual_message)

    def test_message_routing_key(self):
        '''Test messages routing key'''
        self.remoting.call(self.command)

        message = self.pika.published_messages[0]
        routing_key = message.routing_key
        self.assertEquals(routing_key, 'rpc.adventurer') 

class TestRemotingClientReceiveResults(unittest.TestCase):

    def setUp(self):
        self.default_exchange = 'adventurer'
        self.pika = fakepika.SelectConnectionFake()
        self.remoting = RemotingClient(channel=self.pika._channel, exchange=self.default_exchange)

        self.service_name = 'Adventurer'
        self.service = self.remoting.remote_service(self.service_name)
        self.command = self.service.get('bob@smith.com')

        self.headers = pika.BasicProperties(
                correlation_id = self.command.message_id,
                content_type = 'application/json'
                )
        self.body = json.dumps({
            'jsonrpc': '2.0',
            'result': True,
            'id': self.command.message_id
            });


    def test_basic_consume(self):
        '''Consume from queue with callable callback'''

        class CallbackMethod(object):
            def __init__(self):
                self.result = None

            def __call__(self, result):
                self.result = result
        callback = CallbackMethod()

        self.remoting.call(self.command, callback=callback)
        self.pika.inject(self.remoting.queue, self.headers, self.body)
        self.pika.trigger_consume(self.remoting.queue)

        self.assertTrue(callback.result)

    def test_object_callback(self):
        '''Callback is an object with 'result' method'''
        class CallbackMethod(object):
            def __init__(self):
                self.result = None

            def handle_result(self, result):
                self.result = result
        callback = CallbackMethod()

        self.remoting.call(self.command, callback=callback)
        self.pika.inject(self.remoting.queue, self.headers, self.body)
        self.pika.trigger_consume(self.remoting.queue)

        self.assertTrue(callback.result)

    def test_queue_binded(self):
        '''Queue is bound to exchange'''
        search_for = {
                'queue': self.pika._channel.queues.keys()[0],
                'exchange': self.default_exchange,
                'routing_key': 'rpc_reply.' + self.pika._channel.queues.keys()[0],
                }
        binding = self.pika.find_binding(search_for)
        self.assertDictContainsSubset(search_for, binding)


class TestRemotingClientReceiveError(unittest.TestCase):

    def setUp(self):
        self.default_exchange = 'adventurer'
        self.pika = fakepika.SelectConnectionFake()
        self.remoting = RemotingClient(channel=self.pika._channel, exchange=self.default_exchange)

        self.service_name = 'Adventurer'
        self.service = self.remoting.remote_service(self.service_name)
        self.command = self.service.get('bob@smith.com')

        self.headers = pika.BasicProperties(
                correlation_id = self.command.message_id,
                content_type = 'application/json'
                )
        self.jsonrpc = {
            'jsonrpc': '2.0',
            'error': {
                'code': 1,
                'message': 'There was an error',
                'data': False
                },
            'id': self.command.message_id
            }
        self.body = json.dumps(self.jsonrpc);

    def test_object_callback(self):
        '''Error occured and callback is an object with 'error' method'''
        class CallbackMethod(object):
            def __init__(self):
                self.result = None

            def handle_error(self, code, message, data):
                self.result = (code, message, data)
        callback = CallbackMethod()

        self.remoting.call(self.command, callback=callback)
        self.pika.inject(self.remoting.queue, self.headers, self.body)
        self.pika.trigger_consume(self.remoting.queue)

        error = self.jsonrpc['error']
        expected_result = (error['code'], error['message'], error['data'])
        self.assertEquals(expected_result, callback.result)

class TestRemotingClientCreateService(unittest.TestCase):

    def test_create_service(self):
        '''Create a service from the RemotingClient'''
        self.default_exchange = 'adventurer'
        self.pika = fakepika.SelectConnectionFake()
        self.remoting = RemotingClient(channel=self.pika._channel, exchange=self.default_exchange)

        service = self.remoting.service('Gear')
        self.assertIsInstance(service, RemoteService)

        


if __name__ == '__main__':
    unittest.main()

