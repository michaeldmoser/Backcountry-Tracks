from pkg_resources import resource_filename

from bctmessaging.endpoints import MessagingEndPointController
from riak import RiakClient, RiakPbcTransport
from bctks_glbldb import Connection
from bctks_glbldb.catalog import Catalog

from bctmessaging.remoting import RemotingClient
from gpsutils import GPSFormatConverter

from .service import TripsDb
from .coreservice import TripsCoreService
from .commentservice import TripCommentService

class EntryPoint(object):

    def __init__(self, config, env, remoting_client):
        self.config = config
        self.env = env
        self.remoting_client = remoting_client

    def __call__(self):
        bucket_name = self.config['database']['bucket']
        riak = RiakClient(self.config['database']['host'])
        dbcon = Connection(riak)

        return TripsDb(self.remoting_client, riak, bucket_name, self.config['url'],
                converter=GPSFormatConverter, db=dbcon)

class TripsCoreEntry(object):

    def __init__(self, config, env, remoting_client):
        self.config = config
        self.env = env
        self.remoting_client = remoting_client

    def __call__(self):
        riak = RiakClient(host=self.config['database']['host'], port=8087, transport_class=RiakPbcTransport)

        return TripsCoreService(riak, self.config['database']['bucket'])

class TripsCommentsEntry(object):

    def __init__(self, config, env, remoting_client):
        self.config = config
        self.env = env
        self.remoting_client = remoting_client

    def __call__(self):
        riak = RiakClient(host=self.config['database']['host'], port=8087, transport_class=RiakPbcTransport)

        return TripCommentService(riak,
                self.config['database']['trip_bucket'], 
                self.config['database']['comment_bucket'],
                self.config['database']['adventurer_bucket'])


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

    @property
    def stylesheets(self):
        return [resource_filename('trips', 'webroot/trips.css')]

