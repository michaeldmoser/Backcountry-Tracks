import pika
import json


class GearEntryPoint(object):

    def __init__(self, configuration, environ):
        self.environ = environ
        self.config = configuration

        self.usergear = self.__usergear()


    def __usergear(self):
        from gear.usergear import UserGear
        return UserGear

    def __service(self):
        from bctmessaging.services import MessagingServiceController
        return MessagingServiceController

    def __riak(self):
        from riak import RiakClient
        return RiakClient

    def start(self):
        self.environ.open_messaging_channel(self.on_channel_opened)

    def on_channel_opened(self, channel):
        self.channel = channel
        service = self.__service()

        riakclient = self.__riak()
        riak = riakclient(host=self.config['database']['host'])
        usergear = self.usergear(riak, self.config['database']['bucket'])

        self.service = service(self.channel, self.config, usergear)
        self.service.start()

