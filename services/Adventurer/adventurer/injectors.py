import pika.adapters
import riak
import daemon
from lockfile.pidlockfile import PIDLockFile

import service
from adventurer.application import Application

class ControllerInjector(object):
    def __controller(self):
        return service.Controller

    def __pika_connection(self):
        return pika.adapters.SelectConnection

    def __daemoncontext(self):
        return daemon.DaemonContext

    def __pidfile(self):
        return PIDLockFile

    def __application(self):
        return application

    def __call__(self):
        controller_class = self.__controller()
        pika_class = self.__pika_connection()
        daemon_class = self.__daemoncontext()
        pidlockfile = self.__pidfile()
        pidfile = pidlockfile('/var/run/tripplanner/adventurer.pid')
        application = self.__application()

        app = controller_class(
                pika_connection = pika_class,
                pika_params = pika.ConnectionParameters(host = 'localhost'),
                daemonizer = daemon_class,
                pidfile = pidfile,
                application = application
                )
        return app
controller = ControllerInjector()

class ApplicationInjector(object):
    def __riak(self):
        return riak.RiakClient

    def __transport(self):
        return riak.RiakHttpTransport

    def __call__(self):
        riak = self.__riak()
        transport = self.__transport()
        self.riak_client = riak(transport_class = transport)
        bucket = self.riak_client.bucket('adventurers')

        return Application(bucket = bucket)
application = ApplicationInjector()



