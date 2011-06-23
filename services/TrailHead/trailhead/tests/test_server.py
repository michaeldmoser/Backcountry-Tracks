import unittest

from tptesting import environment, fakepika, faketornado, fakedaemonizer

from trailhead.server import TrailHead, RootHandler
from trailhead.register import RegisterHandler
from trailhead.login import LoginHandler
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

        class PidFile(object):
            pass

        self.ioloop = TornadoIoLoopSpy()
        self.webapp = TornadoWebApplication()
        self.daemonizer = Daemonizer()
        self.pidfile = PidFile()
        self.pika_class = fakepika.SelectConnectionFake()

        self.trailhead = TrailHead(
                daemonizer=self.daemonizer,
                ioloop=self.ioloop,
                webapp=self.webapp,
                mqclient=PikaClient(self.pika_class, None), # fake it till you make it
                pidfile=self.pidfile
                )
        self.trailhead.run()
        # FIXME: Need to find a better way to activate this in tests
        self.pika_class.ioloop.start() 

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

class TestTrailHeadReplyQueue(unittest.TestCase):

    def setUp(self):
        self.pika_class = fakepika.SelectConnectionFake()
        self.webapp = faketornado.WebApplicationFake()
        self.trailhead = TrailHead(
                daemonizer=fakedaemonizer.Daemonizer(),
                ioloop=faketornado.ioloop,
                webapp=self.webapp,
                mqclient=PikaClient(self.pika_class, None), # fake it till you make it
                pidfile=fakedaemonizer.PidFile()
                )
        self.trailhead.run()

        # FIXME: Need to find a better way to activate this in tests
        self.pika_class.ioloop.start() 

    def test_reply_queue_created(self):
        '''TrailHead() should create a reply queue for rpc requests'''
        queues = self.pika_class.get_queues()
        self.assertGreater(len(queues), 0)

    def test_reply_queue_declaration(self):
        '''Reply queue created correctly'''
        reply_queue = self.pika_class.get_queues()[0]
        queue = self.pika_class.get_queue_declaration(reply_queue)

        expected_declaration = {
                'exclusive': True,
                'durable': False,
                'auto_delete': True,
                'passive': False
                }
        self.assertDictContainsSubset(expected_declaration, queue)

    def test_reply_queue_name(self):
        '''Name saved for use by handlers'''
        reply_queue = self.pika_class.get_queues()[0]
        self.assertEquals(reply_queue, self.webapp.mq.rpc_reply)


if __name__ == '__main__':
    unittest.main()

