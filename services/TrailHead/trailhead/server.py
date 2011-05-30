from grizzled.os import daemonize

from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from trailhead.register import RegisterHandler

class RootHandler(RequestHandler):
    def get(self):
        pass

class TrailHead(object):

    def __daemonize(self, no_close=False, pidfile=None):
        return daemonize(no_close=no_close, pidfile=pidfile)

    def __tornado_web(self):
        return Application

    def __tornado_io_loop(self):
        return IOLoop

    def run(self):
        self.__daemonize(pidfile='/var/run/tripplanner/trailhead.pid')
        application = self.__tornado_web()
        app = application([
            (r'/', RootHandler),
            (r'/app/register', RegisterHandler),
            ])
        app.listen(8080)

        ioloop = self.__tornado_io_loop()
        ioloop.instance().start()
