from tornado.web import Application, RequestHandler
from trailhead.register import RegisterHandler
from trailhead.login import LoginHandler

class RootHandler(RequestHandler):
    def get(self):
        pass

class TrailHead(object):

    def __init__(self, daemonizer=None, ioloop=None, webapp=None, mqclient=None,
            pidfile=None):
        self.daemonize = daemonizer
        self.ioloop = ioloop
        self.webapp = webapp
        self.mqclient = mqclient
        self.pidfile = pidfile

    def run(self):
        daemon_context = self.daemonize(pidfile=self.pidfile)

        with daemon_context:
            app = self.webapp([
                (r'/', RootHandler),
                (r'/app/register', RegisterHandler),
                (r'/app/login', LoginHandler),
                ])
            app.listen(8080)

            self.ioloop_instance = self.ioloop.IOLoop.instance()
            app.mq = self.mqclient
            self.ioloop_instance.add_timeout(1000, app.mq.connect)
            self.ioloop_instance.start()
