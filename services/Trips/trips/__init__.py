from bctplugins import entrypoint
from .service import TripsDb

class EntryPoint(entrypoint.EntryPoint):
    service = TripsDb

    def __init__(self, configuration, environ):
        entrypoint.EntryPoint.__init__(self, configuration, environ)

