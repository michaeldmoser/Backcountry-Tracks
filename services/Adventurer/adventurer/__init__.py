from pkg_resources import resource_filename
from bctplugins import entrypoint
from riak import RiakClient

from bctmessaging.remoting import RemotingClient
from bctmessaging.endpoints import MessagingEndPointController

from .service import AdventurerRepository
from .mailer import Mailer
from .users import UserService

class EntryPoint(object):

    def __init__(self, configuration, environ, remoting_client):
        self.environ = environ
        self.config = configuration
        self.remoting_client = remoting_client

    def __call__(self):
        bucket_name = self.config['database']['bucket']
        riak = RiakClient(self.config['database']['host'])
        base_url = 'http://' + self.environ.config['hostname']

        smtp_config = self.config.get('smtp', {'host': 'localhost', 'port': 25})
        smtp_host = smtp_config.get('host', 'localhost')
        smtp_port = smtp_config.get('port', 25)
        
        mailer = Mailer(host=smtp_host, port=smtp_port)


        service = AdventurerRepository(bucket_name = bucket_name,
                db = riak, trailhead_url = base_url, mailer=mailer,
                remoting = self.remoting_client)

        return service

class UsersEntryPoint(object):

    def __init__(self, configuration, environ, remoting_client):
        self.environ = environ
        self.config = configuration
        self.remoting_client = remoting_client

    def __call__(self):
        bucket_name = self.config['database']['bucket']
        riak = RiakClient(self.config['database']['host'])

        service = UserService(bucket_name = bucket_name,
                db = riak, remoting = self.remoting_client)

        return service


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





