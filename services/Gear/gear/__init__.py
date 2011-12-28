from pkg_resources import resource_filename

from bctplugins import entrypoint
from bctservices.crud import BasicCRUDService

class UserGear(BasicCRUDService):
    pass

class GearEntryPoint(entrypoint.EntryPoint):
    service = UserGear

class Webroot(object):

    @property
    def javascript_files(self):
        return [resource_filename('gear', 'webroot/gear.js')]

    @property
    def templates(self):
        templates = open(resource_filename('gear', 'webroot/templates.html')).read()
        return templates

