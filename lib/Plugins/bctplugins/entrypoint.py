from bctmessaging.endpoints import MessagingEndPointController
from riak import RiakClient

class EntryPoint(object):
    controller = MessagingEndPointController
    database = RiakClient

    def __init__(self, configuration, environ):
        self.environ = environ
        self.config = configuration

    def start(self):
        messaging_builder = self.environ.get_component_factory('bctks.messaging', 'BackcountryTracks_Messaging', 'MessagingBuilder')
        messaging_builder(self.on_channel_opened)

    def on_channel_opened(self, channel):
        self.channel = channel

        riakclient = self.database
        riak = riakclient(host=self.config['database']['host'])
        service = self.service(riak, self.config['database']['bucket'])

        controller = self.controller(self.channel, self.config, service)
        controller.start()

class MessagingEntryPointFactory(object):
    controller = MessagingEndPointController
    database = RiakClient

    def __init__(self, configuration, environ):
        self.environ = environ
        self.config = configuration

    def assemble_controller(self):
        return MessagingEndPointController

    def assemble_service(self):
        raise NotImplementedError("An assemble_service() method must be provided")

    def start(self):
        messaging_builder = self.environ.get_component_factory('bctks.messaging', 'BackcountryTracks_Messaging', 'MessagingBuilder')
        messaging_builder(self.on_channel_opened)

    def on_channel_opened(self, channel):
        self.channel = channel

        service = self.assemble_service()
        controller_class = self.assemble_controller()
        controller = controller_class(self.channel, self.config, service)
        controller.start()

