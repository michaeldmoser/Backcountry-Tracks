
class PikaClient(object):
    def __init__(self, connection, params, remoting_client):
        self.connection = connection
        self.params = params
        self.remoting_client = remoting_client

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
        self.remoting = self.remoting_client(self.channel)
