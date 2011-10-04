from bctplugins import entrypoint

from gear.usergear import UserGear

class GearEntryPoint(entrypoint.EntryPoint):
    service = UserGear

