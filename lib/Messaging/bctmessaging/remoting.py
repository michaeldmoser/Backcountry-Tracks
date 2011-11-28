import uuid
import pika
import json

class CommandMessage(object):
    def __init__(self, method='', args=None, service='remote', exchange=None):
        self.service = service
        self.method = method
        self.exchange = exchange
        self.persistant = False
        self.content_type = 'application/json-rpc'

        self.args = args
        self.__validate_args()

        self.message_id = str(uuid.uuid4())

    def __validate_args(self):
        if not isinstance(self.args, list) and \
                not isinstance(self.args, tuple) and \
                not isinstance(self.args, dict) and \
                self.args is not None:
            raise ValueError('args must be a list(), tuple(), or dict()')

    def body(self):
        '''Generates a JSON-RPC 2.0 compliant dictionary'''
        json = {
                'jsonrpc': '2.0',
                'method': self.method,
                'id': self.message_id,
                }

        if self.args is not None:
            json['params'] = self.args

        return json

    def __eq__(self, obj):
        return obj.method == self.method and \
                obj.args == self.args and \
                obj.message_id == self.message_id

    def __ne__(self, obj):
        return obj.method != self.method or \
                obj.args != self.args or \
                obj.message_id != self.message_id

class RemoteService(object):
    def __init__(self, service_name):
        self.service_name = service_name

    def __getattr__(self, method_name):
        self.method_name = method_name
        return self

    def __call__(self, *args, **kwargs):
        if args and kwargs:
            raise ValueError('Both positional arguments and named arguments are not supported. Please use one or the other')

        return CommandMessage(
                method=self.method_name,
                args=list(args) if args else kwargs,
                service=self.service_name
                )

class RemotingClient(object):
    def __init__(self, channel=None, exchange='rpc'):
        self.channel = channel
        self.exchange = exchange
        self.__callbacks = dict()
        
        self.channel.queue_declare(callback=self.rpc_queue_declared, exclusive = True, auto_delete = True)

    def rpc_queue_declared(self, queue):
        self.queue = queue.method.queue
        self.channel.queue_bind(exchange=self.exchange, queue=self.queue,
                routing_key='rpc_reply.%s' % self.queue)
        self.channel.basic_consume(self.receive_message, self.queue)

    def receive_message(self, channel, method, headers, body):
        callback = self.__get_callback(headers.correlation_id)
        response = json.loads(body)

        if response.has_key('error'):
            result_handler = self.__handle_error
            callback_method_name = 'handle_error'
        else:
            callback_method_name = 'handle_result'
            result_handler = self.__handle_result

        callback_method = getattr(callback, callback_method_name, None)

        if callable(callback) and not response.has_key('error'):
            callback_method = callback
        elif not callable(callback_method):
            return
        
        result_handler(callback_method, response)

    def __handle_error(self, callback, response):
        error = response['error']
        callback(error['code'], error['message'], error.get('data', None))

    def __handle_result(self, callback, response):
        callback(response['result'])

    def remote_service(self, service):
        '''Create a RemoteService'''
        return RemoteService(service)

    def call(self, command, callback=None):
        '''Send an RPC message through the messaging system'''
        self.__add_callback(command.message_id, callback)
        exchange = self.exchange if command.exchange is None else command.exchange
        properties = pika.BasicProperties(
                reply_to = self.queue,
                content_type = command.content_type,
                delivery_mode = 2 if command.persistant else None,
                correlation_id = command.message_id if callback is not None else None
                )
        self.channel.basic_publish(
                exchange = exchange,
                body = json.dumps(command.body()),
                routing_key = 'rpc.%s' % command.service.lower(),
                properties = properties
                )

    def __get_callback(self, correlation_id):
        return self.__callbacks[correlation_id]

    def __add_callback(self, correlation_id, callback):
        self.__callbacks[correlation_id] = callback

    def service(self, service):
        return RemoteService(service)

