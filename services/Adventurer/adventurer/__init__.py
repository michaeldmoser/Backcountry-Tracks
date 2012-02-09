from pkg_resources import resource_filename
from bctplugins import entrypoint
from riak import RiakClient

from bctmessaging.remoting import RemotingClient
from bctmessaging.endpoints import MessagingEndPointController

from .service import AdventurerRepository
from .mailer import Mailer

class EntryPoint(object):

    def assemble_service(self):
        bucket_name = self.config['database']['bucket']
        riak = RiakClient(self.config['database']['host'])
        base_url = self.environ.config['trailhead_url']

        smtp_config = self.config.get('smtp', {'host': 'localhost', 'port': 25})
        smtp_host = smtp_config.get('host', 'localhost')
        smtp_port = smtp_config.get('port', 25)
        
        mailer = Mailer(host=smtp_host, port=smtp_port)

        remoting_client = RemotingClient(self.service_channel)

        service = AdventurerRepository(bucket_name = bucket_name,
                db = riak, trailhead_url = base_url, mailer=mailer,
                remoting = remoting_client)

        return service

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


class Templates(object):

    @property
    def javascript_files(self):
        return [resource_filename('adventurer', 'webroot/adventurer.js')]

    @property
    def templates(self):
        return open(resource_filename('adventurer', 'webroot/template.html'), 'r').read()

    @property
    def stylesheets(self):
        stylesheets = [
                resource_filename('adventurer', 'webroot/front.css'),
                ]
        return stylesheets





