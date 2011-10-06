from bctmessaging.endpoints import MessagingEndPointController
from riak import RiakClient

class EntryPoint(object):
    controller = MessagingEndPointController
    database = RiakClient

    def __init__(self, configuration, environ):
        self.environ = environ
        self.config = configuration

    def start(self):
        self.environ.open_messaging_channel(self.on_channel_opened)

    def on_channel_opened(self, channel):
        self.channel = channel

        riakclient = self.database
        riak = riakclient(host=self.config['database']['host'])
        service = self.service(riak, self.config['database']['bucket'])

        controller = self.controller(self.channel, self.config, service)
        controller.start()

