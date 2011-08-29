import pika
import json


class EntryPoint(object):

    def __init__(self, configuration, environ):
        self.environ = environ
        self.config = configuration

        self.repository = self.__repository()

    def __repository(self):
        from .model import AdventurerRepository
        return AdventurerRepository

    def __service(self):
        from .service import AdventurerService
        return AdventurerService

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
        repository = self.repository(riak, self.config['database']['bucket'])

        self.service = service(self.channel, self.config, repository)
        self.service.start()

