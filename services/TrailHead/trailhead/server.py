from tornado.web import Application, RequestHandler
from trailhead.register import RegisterHandler
from trailhead.register import ActivateHandler
from trailhead.login import LoginHandler
from trailhead.gear import UserGearListHandler

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

        settings = {
            'cookie_secret': "psx4I0LFuKEZhL2un7HUhoDMq7UR2ZUV2ja",
            'login_url': "/"
            }

        with daemon_context:
            app = self.webapp([
                (r'/', RootHandler),
                (r'/app/register', RegisterHandler),
                (r'/app/activate/(.*)/(.*)', ActivateHandler),
                (r'/app/login', LoginHandler),
                (r'/app/users/(.*)/gear', UserGearListHandler),
                ], **settings)
            app.listen(8080)

        self.ioloop_instance = self.ioloop.IOLoop.instance()
        app.mq = self.mqclient
        self.ioloop_instance.add_timeout(1000, app.mq.connect)
        self.ioloop_instance.start()
