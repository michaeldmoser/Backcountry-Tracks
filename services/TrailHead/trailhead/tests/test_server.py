import unittest

from tptesting import environment

from trailhead.server import TrailHead, RootHandler
from trailhead.register import RegisterHandler

class TrailHeadStub(TrailHead):
    def __init__(self):
        super(TrailHeadStub, self).__init__()

    def _TrailHead__daemonize(self, no_close=False, pidfile=None):
        pass

    def _TrailHead__tornado_web(self):
        class TornadoWebApplicationStub(object):
            def __init__(self, *args, **kwargs):
                pass

            def listen(self, port):
                pass

        return TornadoWebApplicationStub

    def _TrailHead__tornado_io_loop(self):
        class TornadoIOLoopStub(object):
            def instance(self):
                class TornadoLoopInstanceStub(object):
                    def start(self):
                        pass

                return TornadoLoopInstanceStub()

        return TornadoIOLoopStub()

class TestTrailHeadDaemonized(unittest.TestCase):
    def setUp(self):
        self.environ = environment.create()

        class TestTrailHead(TrailHeadStub):
            def __init__(self):
                super(TestTrailHead, self).__init__()
                self.daemonized = False

            def _TrailHead__daemonize(self, no_close=False, pidfile=None):
                self.daemonized = True
                self.daemonize_args = {'no_close': no_close, 'pidfile': pidfile}

        self.TestTrailHead = TestTrailHead

    def tearDown(self):
        pass

    def test_run_should_daemonize(self):
        '''TrailHead.run() should daemonize'''
        testtrailhead = self.TestTrailHead()
        testtrailhead.run()

        assert(testtrailhead.daemonized)

    def test_pidfile_argument(self):
        '''Properly creates a pidfile'''
        testtrailhead = self.TestTrailHead()
        testtrailhead.run()

        actual_pidfile = testtrailhead.daemonize_args['pidfile'] 
        expected_pidfile = self.environ.trailhead['pidfile']
        self.assertEquals(actual_pidfile, expected_pidfile)

class TestTrailHeadTornado(unittest.TestCase):
    def setUp(self):
        self.environ = environment.create()


        class TestTrailHead(TrailHeadStub):
            def __init__(self):
                super(TestTrailHead, self).__init__()

            def _TrailHead__tornado_web(self):
                class TornadoWebApplication(object):
                    def __init__(twaself, routes):
                        self.routes = routes

                    def listen(twaself, port):
                        self.port = port

                return TornadoWebApplication

            def _TrailHead__tornado_io_loop(self):
                class TornadoIOLoop(object):
                    def instance(tioself):
                        class TornadoLoopInstance(object):
                            def __init__(tioself):
                                self.start_called = False
                            def start(tioself):
                                self.start_called = True

                        return TornadoLoopInstance()

                return TornadoIOLoop()


        self.testtrailhead = TestTrailHead()
        self.testtrailhead.run()


    def tearDown(self):
        pass

    def test_adds_root_handler(self):
        """Adds a root handler to Tornado"""
        expected_route = (r'/', RootHandler)
        routes = self.testtrailhead.routes

        try:
            routes.index(expected_route)
        except ValueError, e:
            self.fail(str(e))

    def test_listens_on_port_8080(self):
        '''Setup to listen on port 8080'''
        self.assertEquals(8080, self.testtrailhead.port)

    def test_start_tornado_io_loop(self):
        '''Needs to start the tornado io loop'''
        assert(self.testtrailhead.start_called)

    def test_adds_register_handler(self):
        '''Add a register handler to Tornado'''
        expected_route = (r'/app/register', RegisterHandler)
        routes = self.testtrailhead.routes

        try:
            routes.index(expected_route)
        except ValueError, e:
            self.fail(str(e))

if __name__ == '__main__':
    unittest.main()

