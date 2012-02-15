from .services import ServiceLookup
from bctmessaging.remoting import RemotingClient
from .endpoint import MessagingEndpointServiceController


class EntryPoint(object):

    def __init__(self, config, env):
        self.env = env
        self.config = config

    def start(self):
        self.env.open_messaging_channel(self.on_recv_channel_opened)

    def on_recv_channel_opened(self, channel):
        self.recv_channel = channel
        
        connection = channel.transport.connection
        connection.channel(self.on_pub_channel_opened)

    def on_pub_channel_opened(self, channel):
        self.pub_channel = channel
        
        connection = channel.transport.connection
        connection.channel(self.on_reply_channel_opened)

    def on_reply_channel_opened(self, channel):
        self.reply_channel = channel

        self.create_service()

    def create_service(self):
        remoting_client = RemotingClient(self.reply_channel)
        services = ServiceLookup(self.config['services'], self.env, remoting_client)

        endpoint = MessagingEndpointServiceController(self.recv_channel, self.recv_channel,
                self.config, services, remoting_client)
        endpoint.start()







