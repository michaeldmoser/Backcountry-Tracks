import unittest

from tptesting import environment, fakepika, faketornado, fakedaemonizer

from trailhead.server import TrailHead, RootHandler
from trailhead.mq import PikaClient

class TestTrailHeadTornado(unittest.TestCase):
    '''
    This test case is testing the basic startup procedures of
    the TrailHead app server. Note that it may be fragile due
    to the heavy reliance on behavioral testing.
    '''

    def setUp(self):
        self.environ = environment.create()

        self.ioloop = faketornado.ioloop
        self.webapp = faketornado.WebApplicationFake()
        self.pika_class = fakepika.SelectConnectionFake()

        self.config = {
                'port': 8081,
                'address': 'localhost',
                'cookie_secret': 'trailhead',
                'login_url': '/app/login',
                'handlers': []
                }

        self.trailhead = TrailHead(
                ioloop=self.ioloop,
                webapp=self.webapp,
                mqclient=PikaClient(self.pika_class, None),
                config=self.config
                )
        self.trailhead.run()

    def test_adds_root_handler(self):
        """Adds a root handler to Tornado"""
        expected_route = (r'/', RootHandler)
        routes = self.webapp.handlers

        try:
            routes.index(expected_route)
        except ValueError, e:
            self.fail(str(e))

    def test_settings(self):
        '''Sets the correct settings for Tornado'''
        expected_settings = self.config.copy()
        del expected_settings['handlers']
        self.assertEquals(expected_settings, self.webapp.settings)

    def test_listens_on_configured_port(self):
        '''Setup to listen on configured port'''
        correct_usage = self.webapp.verify_usage(self.webapp.listen,
                (self.config['port'],), {'address': self.config['address']})
        self.assertTrue(correct_usage)

    def test_adds_pika_to_application(self):
        '''PikaClient should be on the application instance'''
        self.assertIsInstance(self.webapp.mq, PikaClient)

    def test_connects_to_mq(self):
        '''Should create a connection to the message queue'''
        self.assertTrue(self.pika_class.was_called(self.pika_class.__init__))

class TestTrailHeadConfiguration(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()
        self.ioloop = faketornado.ioloop
        self.webapp = faketornado.WebApplicationFake()
        self.pika_class = fakepika.SelectConnectionFake()


    def instantiate_trailhead(self, config):
        trailhead = TrailHead(
                ioloop=self.ioloop,
                webapp=self.webapp,
                mqclient=PikaClient(self.pika_class, None),
                config=config
                )
        trailhead.run()

    def test_listen_defaults(self):
        '''Port and Address configuration default to localhost:8080'''
        config = {
                'cookie_secret': 'trailhead',
                'login_url': '/app/login'
                }
        self.instantiate_trailhead(config)


        correct_usage = self.webapp.verify_usage(self.webapp.listen,
                (8080,), {'address': 'localhost'})
        self.assertTrue(correct_usage)

    def test_cookie_defaults(self):
        '''Test cookie_secret is set to a sane default'''
        config = {
                'login_url': '/app/login'
                }
        self.instantiate_trailhead(config)

        actual_secret = self.webapp.settings['cookie_secret']
        expected_secret = 'tde2HDb+R9evlg/vUMDlaBUTPSMF1kgtnpKhvkgOXNQ='
        self.assertEquals(expected_secret, actual_secret)

    def test_login_url_default(self):
        '''login_url should default to /app/login'''
        self.instantiate_trailhead({})

        actual_url = self.webapp.settings['login_url']
        expected_url = '/app/login'
        self.assertEquals(expected_url, actual_url)

class TestHandlerLoading(unittest.TestCase):

    def test_loads_handler(self):
        '''Loads the configured handler'''
        self.environ = environment.create()
        self.ioloop = faketornado.ioloop
        self.webapp = faketornado.WebApplicationFake()
        self.pika_class = fakepika.SelectConnectionFake()

        config = {
                'handlers': [
                    ['/app/login', 'Adventurer/login'] ,
                    ['/app/activate/(.*)/(.*)', 'Adventurer/activate'],
                    ['/app/trips/([0-9a-f-]+)$', 'Trips/trip']
                    ]
                }

        class LoginHandler(object):
            pass

        class ActivateHandler(object):
            pass

        class TripHandler(object):
            pass

        class LoadEntryPoint(object):
            def __init__(self):
                self.entry_points = {
                        'Adventurer': {
                            'tripplanner.trailhead.handler': {
                                'login': LoginHandler,
                                'activate': ActivateHandler
                                }
                            },
                        'Trips': {
                            'tripplanner.trailhead.handler': {
                                'trip': TripHandler
                                }
                            }
                        }

            def __call__(self, dist, group, name):
                try:
                    dist = self.entry_points[dist]
                    group = dist[group]
                    handler = group[name]
                except KeyError:
                    raise ImportError

                return handler
        load_entry_point = LoadEntryPoint()

        trailhead = TrailHead(
                ioloop=self.ioloop,
                webapp=self.webapp,
                mqclient=PikaClient(self.pika_class, None),
                config=config,
                load_entry_point = load_entry_point
                )
        trailhead.run()

        self.webapp.handlers.pop(0)
        expected_handlers = [
                ('/app/login', LoginHandler),
                ('/app/activate/(.*)/(.*)', ActivateHandler),
                ('/app/trips/([0-9a-f-]+)$', TripHandler),
                ]
        self.assertEquals(expected_handlers, self.webapp.handlers)


if __name__ == '__main__':
    unittest.main()

