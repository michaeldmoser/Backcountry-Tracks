from bctplugins import entrypoint

from .model import AdventurerRepository

class EntryPoint(entrypoint.EntryPoint):
    service = AdventurerRepository

