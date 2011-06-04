import unittest

from tptesting import environment

from trailhead.server import TrailHead, RootHandler
from trailhead.register import RegisterHandler

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

            def __call__(self, routes):
                '''
                Use this so the instance can act like a class but allows us
                to record calls
                '''
                self.routes = routes
                return self

        class Daemonizer(object):
            def __init__(self):
                self.daemonized = False

            def __call__(self, pidfile=None):
                self.pidfile = pidfile
                return self

            def __enter__(self):
                self.daemonized = True
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                pass

        class PikaClientStub(object):
            def connect(stub):
                stub.connected = True
        self.pikastub = PikaClientStub

        class PidFile(object):
            pass

        self.ioloop = TornadoIoLoopSpy()
        self.webapp = TornadoWebApplication()
        self.daemonizer = Daemonizer()
        self.pidfile = PidFile()

        self.trailhead = TrailHead(
                daemonizer=self.daemonizer,
                ioloop=self.ioloop,
                webapp=self.webapp,
                mqclient=PikaClientStub(),
                pidfile=self.pidfile
                )
        self.trailhead.run()

    def tearDown(self):
        pass

    def test_pidfile_argument(self):
        '''Properly creates a pidfile'''
        self.assertEquals(self.pidfile, self.daemonizer.pidfile)

    def test_process_daemonizes(self):
        '''The trailhead process should daemonize'''
        assert(self.daemonizer.daemonized)


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

    def test_adds_pika_to_application(self):
        '''PikaClient should be on the application instance'''
        assert(isinstance(self.webapp.mq, self.pikastub))

    def test_connects_to_mq(self):
        '''Should create a connection to the message queue'''
        assert(self.webapp.mq.connected)


if __name__ == '__main__':
    unittest.main()

