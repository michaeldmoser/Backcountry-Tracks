from bctplugins import entrypoint
from trips.db import TripsDb

class EntryPoint(entrypoint.EntryPoint):
    service = TripsDb

    def __init__(self, configuration, environ):
        entrypoint.EntryPoint.__init__(self, configuration, environ)


