
class EntryPoint(object):

    def __init__(self, configuration, environ):
        self.environ = environ
        self.config = configuration

        self.db = self.__db()


    def __db(self):
        from trips.db import TripsDb
        return TripsDb

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
        db = self.db(riak, self.config['database']['bucket'])

        self.service = service(self.channel, self.config, db)
        self.service.start()



