import pika.adapters
import daemon
from lockfile.pidlockfile import PIDLockFile

import service

class ApplicationInjector(object):
    def __application(self):
        return service.Application

    def __pika_connection(self):
        return pika.adapters.SelectConnection

    def __daemoncontext(self):
        return daemon.DaemonContext

    def __pidfile(self):
        return PIDLockFile

    def __call__(self):
        application_class = self.__application()
        pika_class = self.__pika_connection()
        daemon_class = self.__daemoncontext()
        pidlockfile = self.__pidfile()
        pidfile = pidlockfile('/var/run/tripplanner/adventurer.pid')

        app = application_class(
                pika_connection = pika_class,
                pika_params = pika.ConnectionParameters(host = 'localhost'),
                daemonizer = daemon_class,
                pidfile = pidfile
                )
        return app
application = ApplicationInjector()
    

