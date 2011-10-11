from bctplugins import entrypoint
from bctservices.crud import BasicCRUDService

class UserGear(BasicCRUDService):
    pass

class GearEntryPoint(entrypoint.EntryPoint):
    service = UserGear

