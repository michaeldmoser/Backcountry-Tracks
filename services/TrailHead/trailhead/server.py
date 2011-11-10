import yaml

from tornado.web import Application, RequestHandler
from trailhead.register import RegisterHandler
from trailhead.register import ActivateHandler
from trailhead.login import LoginHandler
from trailhead.gear import UserGearListHandler
from trailhead.user import UserHandler
from trailhead.trips import TripsHandler, TripHandler

class RootHandler(RequestHandler):
    def get(self):
        pass

class TrailHead(object):

    def __init__(self, ioloop=None, webapp=None, mqclient=None, config={}):
        self.ioloop = ioloop
        self.webapp = webapp
        self.mqclient = mqclient
        self.config = config

        self.default_config = {
                'cookie_secret': 'tde2HDb+R9evlg/vUMDlaBUTPSMF1kgtnpKhvkgOXNQ=',
                'login_url': '/app/login'
                }

    def run(self):
        settings = self.default_config.copy()
        settings.update(self.config)
        

        app = self.webapp([
            (r'/', RootHandler),
            (r'/app/register', RegisterHandler),
            (r'/app/activate/(.*)/(.*)', ActivateHandler),
            (r'/app/login', LoginHandler),
            (r'/app/users/([^/]+)/gear$', UserGearListHandler),
            (r'/app/users/([^/]+)/gear/([^/]+)$', UserGearListHandler),
            (r'/app/user', UserHandler),
            (r'/app/trips$', TripsHandler),
            (r'/app/trips/([0-9a-f-]+)$', TripHandler),
            ], **settings)
        
        port = self.config.get('port', 8080)
        address = self.config.get('address', 'localhost')
        app.listen(port, address=address)

        self.ioloop_instance = self.ioloop.IOLoop.instance()
        app.mq = self.mqclient
        self.ioloop_instance.add_timeout(1000, app.mq.connect)
        self.ioloop_instance.start()

