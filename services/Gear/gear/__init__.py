from pkg_resources import resource_filename

from bctplugins import entrypoint
from bctservices.crud import BasicCRUDService
from riak import RiakClient, RiakPbcTransport

from bctks_glbldb import Connection
from gear.service import AdventurerGearService
from gear.objects import AdventurerInventory

class AdventurerGear(BasicCRUDService):
    pass

class GearEntryPoint(object):

    def __init__(self, config, env, remoting):
        self.config = config
        self.env = env
        self.remoting = remoting

    def __call__(self):
        riak = RiakClient(host=self.config['database']['host'], port=8087, transport_class=RiakPbcTransport)
        dbcon = Connection(riak)
        realm = dbcon.Realm(self.config['database']['bucket'])

        def inventory_generator(adventurer):
            return AdventurerInventory(realm, adventurer)

        service = AdventurerGearService(inventory_generator)

        return service

class Webroot(object):

    @property
    def javascript_files(self):
        return [resource_filename('gear', 'webroot/gear.js')]

    @property
    def templates(self):
        templates = open(resource_filename('gear', 'webroot/templates.html')).read()
        return templates

