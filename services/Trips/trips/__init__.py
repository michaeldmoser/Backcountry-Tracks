from bctmessaging.endpoints import MessagingEndPointController
from riak import RiakClient

from bctplugins import entrypoint
from bctmessaging.remoting import RemotingClient

from .service import TripsDb

class EntryPoint(object):

    def assemble_service(self):
        bucket_name = self.config['database']['bucket']
        riak = RiakClient(self.config['database']['host'])

        remoting_client = RemotingClient(self.service_channel)

        return TripsDb(remoting_client, riak, bucket_name)

    def __init__(self, configuration, environ):
        self.environ = environ
        self.config = configuration

    def start(self):
        self.environ.open_messaging_channel(self.on_service_channel_opened)

    def on_service_channel_opened(self, channel):
        self.service_channel = channel
        connection = channel.transport.connection
        connection.channel(self.on_controller_channel_opened)

    def on_controller_channel_opened(self, channel):
        self.channel = channel

        service = self.assemble_service()
        controller = MessagingEndPointController(self.channel, self.config, service)
        controller.start()

