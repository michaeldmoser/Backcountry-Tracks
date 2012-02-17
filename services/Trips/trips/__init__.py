from pkg_resources import resource_filename

from bctmessaging.endpoints import MessagingEndPointController
from riak import RiakClient

from bctplugins import entrypoint
from bctmessaging.remoting import RemotingClient
from gpsutils import GPSFormatConverter

from .service import TripsDb

class EntryPoint(object):

    def __init__(self, config, env, remoting_client):
        self.config = config
        self.env = env
        self.remoting_client = remoting_client

    def __call__(self):
        bucket_name = self.config['database']['bucket']
        riak = RiakClient(self.config['database']['host'])

        return TripsDb(self.remoting_client, riak, bucket_name, self.config['url'],
                converter=GPSFormatConverter)


class Webroot(object):

    @property
    def javascript_files(self):
        return [
                resource_filename('trips', 'webroot/trip_gear.js'),
                resource_filename('trips', 'webroot/trips.js')
                ]

    @property
    def templates(self):
        return open(resource_filename('trips', 'webroot/templates.html')).read()

