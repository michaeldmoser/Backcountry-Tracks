import unittest

from tptesting import environment, fakepika, faketornado, fakedaemonizer

from trailhead.server import TrailHead, RootHandler
from trailhead.register import RegisterHandler
from trailhead.gear import UserGearListHandler
from trailhead.trips import TripsHandler, TripHandler
from trailhead.login import LoginHandler
from trailhead.user import UserHandler
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
                'login_url': '/app/login'
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
        self.assertEquals(self.config, self.webapp.settings)

    def test_listens_on_configured_port(self):
        '''Setup to listen on configured port'''
        correct_usage = self.webapp.verify_usage(self.webapp.listen,
                (self.config['port'],), {'address': self.config['address']})
        self.assertTrue(correct_usage)

    def test_adds_register_handler(self):
        '''Add a register handler to Tornado'''
        expected_route = (r'/app/register', RegisterHandler)
        routes = self.webapp.handlers

        try:
            routes.index(expected_route)
        except ValueError, e:
            self.fail(str(e))

    def test_adds_gear_list_handler(self):
        '''Adds handler for user gear list'''
        expected_route = (r'/app/users/([^/]+)/gear$', UserGearListHandler)

        routes = self.webapp.handlers

        try:
            routes.index(expected_route)
        except ValueError, e:
            self.fail(str(e))

    def test_adds_gear_handler(self):
        '''Adds handler for user gear'''
        expected_route = (r'/app/users/([^/]+)/gear/([^/]+)$', UserGearListHandler)

        routes = self.webapp.handlers

        try:
            routes.index(expected_route)
        except ValueError, e:
            self.fail(str(e))

    def test_adds_trips_handler(self):
        '''Adds handler for working with collections of trips'''
        expected_route = (r'/app/trips$', TripsHandler)

        routes = self.webapp.handlers

        try:
            routes.index(expected_route)
        except ValueError, e:
            self.fail(str(e))

    def test_adds_trip_handler(self):
        '''Adds handler for managing a trip'''
        expected_route = (r'/app/trips/([0-9a-f-]+)$', TripHandler)

        routes = self.webapp.handlers

        try:
            routes.index(expected_route)
        except ValueError, e:
            self.fail(str(e))

    def test_adds_pika_to_application(self):
        '''PikaClient should be on the application instance'''
        self.assertIsInstance(self.webapp.mq, PikaClient)

    def test_connects_to_mq(self):
        '''Should create a connection to the message queue'''
        self.assertTrue(self.pika_class.was_called(self.pika_class.__init__))

    def test_adds_login_handler(self):
        '''The login handler should be added to the routes'''
        expected_route = (r'/app/login', LoginHandler)
        routes = self.webapp.handlers

        try:
            routes.index(expected_route)
        except ValueError, e:
            self.fail(str(e))

    def test_adds_user_handler(self):
        '''The UserHandler should be added to the routes'''
        expected_route = (r'/app/user', UserHandler)
        routes = self.webapp.handlers
        try:
            routes.index(expected_route)
        except ValueError, e:
            self.fail(str(e))

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


if __name__ == '__main__':
    unittest.main()

