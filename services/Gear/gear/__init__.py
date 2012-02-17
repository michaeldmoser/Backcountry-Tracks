from pkg_resources import resource_filename

from bctplugins import entrypoint
from bctservices.crud import BasicCRUDService
from riak import RiakClient

class UserGear(BasicCRUDService):
    pass

class GearEntryPoint(object):

    def __init__(self, config, env, remoting):
        self.config = config
        self.env = env
        self.remoting = remoting

    def __call__(self):
        riak = RiakClient(host=self.config['database']['host'])
        service = UserGear(riak, self.config['database']['bucket'])

        return service

class Webroot(object):

    @property
    def javascript_files(self):
        return [resource_filename('gear', 'webroot/gear.js')]

    @property
    def templates(self):
        templates = open(resource_filename('gear', 'webroot/templates.html')).read()
        return templates

