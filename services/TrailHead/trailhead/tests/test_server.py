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

        class TornadoIoLoopInstance(object):
            def __init__(self):
                self.start_called = False

            def start(self):
                self.start_called = True

            def add_timeout(spy, timeout, connect):
                spy.connect_timeout = timeout
                spy.connect_callback = connect
                connect()

        class TornadoIoLoopSpy(object):
            def __init__(spy):
                class IOLoopspy(object):
                    def instance(self):
                        spy.ioloop_instance = TornadoIoLoopInstance()

                        return spy.ioloop_instance
                spy.IOLoop = IOLoopspy()

        class TornadoWebApplication(object):
            def __init__(self):
                self.port = None

            def listen(self, port):
                self.port = port

            def __call__(self, routes, **args):
                '''
                Use this so the instance can act like a class but allows us
                to record calls
                '''
                self.routes = routes
                return self

        self.ioloop = TornadoIoLoopSpy()
        self.webapp = TornadoWebApplication()
        self.pika_class = fakepika.SelectConnectionFake()

        self.trailhead = TrailHead(
                ioloop=self.ioloop,
                webapp=self.webapp,
                mqclient=PikaClient(self.pika_class, None), # fake it till you make it
                )
        self.trailhead.run()
        # FIXME: Need to find a better way to activate this in tests
        self.pika_class.ioloop.start()

    def tearDown(self):
        pass

    def test_adds_root_handler(self):
        """Adds a root handler to Tornado"""
        expected_route = (r'/', RootHandler)
        routes = self.webapp.routes

        try:
            routes.index(expected_route)
        except ValueError, e:
            self.fail(str(e))

    def test_listens_on_port_8080(self):
        '''Setup to listen on port 8080'''
        self.assertEquals(8080, self.webapp.port)

    def test_start_tornado_io_loop(self):
        '''Needs to start the tornado io loop'''
        assert(self.ioloop.ioloop_instance.start_called)

    def test_adds_register_handler(self):
        '''Add a register handler to Tornado'''
        expected_route = (r'/app/register', RegisterHandler)
        routes = self.webapp.routes

        try:
            routes.index(expected_route)
        except ValueError, e:
            self.fail(str(e))

    def test_adds_gear_list_handler(self):
        '''Adds handler for user gear list'''
        expected_route = (r'/app/users/([^/]+)/gear$', UserGearListHandler)

        routes = self.webapp.routes

        try:
            routes.index(expected_route)
        except ValueError, e:
            self.fail(str(e))

    def test_adds_gear_handler(self):
        '''Adds handler for user gear'''
        expected_route = (r'/app/users/([^/]+)/gear/([^/]+)$', UserGearListHandler)

        routes = self.webapp.routes

        try:
            routes.index(expected_route)
        except ValueError, e:
            self.fail(str(e))

    def test_adds_trips_handler(self):
        '''Adds handler for working with collections of trips'''
        expected_route = (r'/app/trips$', TripsHandler)

        routes = self.webapp.routes

        try:
            routes.index(expected_route)
        except ValueError, e:
            self.fail(str(e))

    def test_adds_trip_handler(self):
        '''Adds handler for managing a trip'''
        expected_route = (r'/app/trips/([0-9a-f-]+)$', TripHandler)

        routes = self.webapp.routes

        try:
            routes.index(expected_route)
        except ValueError, e:
            self.fail(str(e))

    def test_adds_pika_to_application(self):
        '''PikaClient should be on the application instance'''
        self.assertIsInstance(self.webapp.mq, PikaClient)

    def test_connects_to_mq(self):
        '''Should create a connection to the message queue'''
        self.assertIn('connected', self.pika_class.usage)

    def test_adds_login_handler(self):
        '''The login handler should be added to the routes'''
        expected_route = (r'/app/login', LoginHandler)
        routes = self.webapp.routes

        try:
            routes.index(expected_route)
        except ValueError, e:
            self.fail(str(e))

    def test_adds_user_handler(self):
        '''The UserHandler should be added to the routes'''
        expected_route = (r'/app/user', UserHandler)
        routes = self.webapp.routes
        try:
            routes.index(expected_route)
        except ValueError, e:
            self.fail(str(e))

if __name__ == '__main__':
    unittest.main()

