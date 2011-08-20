import pika
import json


class GearEntryPoint(object):

    def __init__(self, environ, configuration):
        self.environ = environ
        self.config = configuration

        self.usergear = self.__usergear()


    def __usergear(self):
        from gear.usergear import UserGear
        return UserGear

    def __gearservice(self):
        from gear.service import GearService
        return GearService

    def start(self):
        self.environ.open_messaging_channel(self.on_channel_opened)

    def on_channel_opened(self, channel):
        self.channel = channel
        service = self.__gearservice()
        self.service = service(self.channel, self.config, self.usergear())

        self.service.start()

