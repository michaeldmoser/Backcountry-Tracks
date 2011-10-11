from bctservices.crud import BasicCRUDService
from bctplugins import entrypoint

class AdventurerRepository(BasicCRUDService):
    pass

class EntryPoint(entrypoint.EntryPoint):
    service = AdventurerRepository




