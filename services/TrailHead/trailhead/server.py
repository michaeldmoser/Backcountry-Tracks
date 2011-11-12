import yaml
from pkg_resources import load_entry_point

from tornado.web import Application, RequestHandler
#from trailhead.register import RegisterHandler
#from trailhead.register import ActivateHandler
#from trailhead.gear import UserGearListHandler
#from trailhead.user import UserHandler
#from trailhead.trips import TripsHandler, TripHandler


class RootHandler(RequestHandler):
    def get(self):
        pass

class TrailHead(object):

    def __init__(self, ioloop=None, webapp=None, mqclient=None,
            load_entry_point=load_entry_point, config={}):
        self.ioloop = ioloop
        self.webapp = webapp
        self.mqclient = mqclient
        self.config = config
        self.load_entry_point = load_entry_point

        self.default_config = {
                'cookie_secret': 'tde2HDb+R9evlg/vUMDlaBUTPSMF1kgtnpKhvkgOXNQ=',
                'login_url': '/app/login'
                }

    def __get_handlers_list(self):
        handler_configs = self.config.get('handlers', [])

        handlers = [
                (r'/', RootHandler),
                ]
        for handler_config in handler_configs:
            dist, name = handler_config[1].split('/')
            handler = self.load_entry_point(dist, 'tripplanner.trailhead.handler', name)
            handlers.append((handler_config[0], handler))

        return handlers

    def __get_settings(self):
        settings = self.default_config.copy()
        settings.update(self.config)
        try:
            del settings['handlers']
        except KeyError:
            pass

        return settings

    def run(self):
        settings = self.__get_settings()
        handlers = self.__get_handlers_list()
        app = self.webapp(handlers, **settings)
        app.mq = self.mqclient
        
        port = self.config.get('port', 8080)
        address = self.config.get('address', 'localhost')
        app.listen(port, address=address)

        self.ioloop_instance = self.ioloop.IOLoop.instance()
        self.ioloop_instance.add_timeout(1000, app.mq.connect)
        self.ioloop_instance.start()

