
class PikaClient(object):
    def __init__(self, connection, params):
        self.connection = connection
        self.params = params

        self.rpc_replies = dict()

    def connect(self):
        '''
        Establish a connection setup the rest of the Pika client
        '''
        self.connection(self.params, on_open_callback=self.on_connected)

    def on_connected(self, connection):
        self.connection = connection
        self.open_channel()

    def open_channel(self):
        '''
        Creates a channel
        '''
        self.connection.channel(self.on_channel_opened)

    def on_channel_opened(self, channel):
        self.channel = channel
        self.create_rpc_reply_queue()

    def create_rpc_reply_queue(self):
        self.channel.queue_declare(callback=self.rpc_queue_declared, exclusive = True, auto_delete = True)

    def rpc_queue_declared(self, queue):
        self.rpc_reply = queue.method.queue
        self.bind_reply_queue()
        self.consume_reply_messages()

    def bind_reply_queue(self):
        self.channel.queue_bind(exchange='adventurer', queue=self.rpc_reply,
                routing_key='adventurer.login.%s' % self.rpc_reply)
        self.channel.queue_bind(exchange='registration', queue=self.rpc_reply,
                routing_key='registration.activate.%s' % self.rpc_reply)
        self.channel.queue_bind(exchange='registration', queue=self.rpc_reply,
                routing_key='registration.register.%s' % self.rpc_reply)

    def consume_reply_messages(self):
        self.channel.basic_consume(self.receive_message, queue=self.rpc_reply)

    def receive_message(self, channel, method, headers, body):
        correlation_id = headers.correlation_id
        self.rpc_replies[correlation_id](headers, body)

    def register_rpc_reply(self, correlation_id, callback):
        self.rpc_replies[correlation_id] = callback

