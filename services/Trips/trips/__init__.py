from bctplugins import entrypoint
from bctservices.crud import BasicCRUDService

class TripsDb(BasicCRUDService):
    pass

class EntryPoint(entrypoint.EntryPoint):
    service = TripsDb

    def __init__(self, configuration, environ):
        entrypoint.EntryPoint.__init__(self, configuration, environ)

