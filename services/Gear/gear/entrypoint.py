import pika
import json


class GearEntryPoint(object):

    def __init__(self, channel, configuration):
        self.channel = channel
        self.config = configuration

        self.usergear = self.__usergear()

        service = self.__gearservice()
        self.service = service(channel, self.config, self.usergear())

    def __usergear(self):
        from gear.usergear import UserGear
        return UserGear

    def __gearservice(self):
        from gear.service import GearService
        return GearService

    def start(self):
        self.service.start()

