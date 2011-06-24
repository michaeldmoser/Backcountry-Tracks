import pdb

class PikaClient(object):
    def __init__(self, connection, params):
        self.connection = connection
        self.params = params

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

    def bind_reply_queue(self):
        self.channel.queue_bind(exchange='adventurer', queue=self.rpc_reply,
                routing_key='adventurer.login.%s' % self.rpc_reply)
