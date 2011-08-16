import pika
import json

from gear.usergear import UserGear

class GearEntryPoint(object):

    def __init__(self, channel, configuration):
        self.channel = channel
        self.config = configuration

        self.usergear = self.__usergear()

        service = self.__gearservice()
        self.service = service(channel, self.config, self.usergear())

    def start(self):
        self.service.start()

