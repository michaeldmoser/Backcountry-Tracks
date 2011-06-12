import unittest

import json
from pika import frame, spec
import pika

from tptesting import environment, fakepika

from adventurer.service import Controller

class TestControllerDaemon(unittest.TestCase):
    def setUp(self):
        class DaemonContextSpy(object):
            def __init__(spy):
                spy.daemonized = False

            def __call__(spy, pidfile=None):
                spy.pidfile = pidfile
                return spy 

            def __enter__(spy):
                spy.daemonized = True
                return spy

            def __exit__(self, exc_type, exc_value, trackback):
                pass
        self.DaemonContextSpy = DaemonContextSpy

        class PIDFileStub(object):
            pass
        self.pidfile = PIDFileStub()

        class AdventurerApplicationStub(object):
            def register(spy, data):
                pass

        self.daemonizer = self.DaemonContextSpy()
        app = Controller(
                daemonizer = self.daemonizer,
                pidfile = self.pidfile,
                pika_params = dict(),
                pika_connection = fakepika.SelectConnectionFake(),
                application = AdventurerApplicationStub
                )
        app.run()

    def test_process_daemonizes(self):
        """The adverturer process should daemonize"""
        assert self.daemonizer.daemonized

    def test_correct_pidfile(self):
        '''Should set the correct pidfile path'''
        self.assertEquals(self.daemonizer.pidfile, self.pidfile)

class TestControllerPika(unittest.TestCase):
    def setUp(self):
        class DaemonContextStub(object):
            def __init__(spy, pidfile=None):
                pass

            def __enter__(spy):
                return spy

            def __exit__(self, exc_type, exc_value, trackback):
                pass
        self.DaemonContextStub = DaemonContextStub

        self.pika_connection = fakepika.SelectConnectionFake()
        self.parameters = dict(host='localhost')

        class AdventurerApplicationStub(object):
            def register(spy, data):
                pass

        app = Controller(
                daemonizer = self.DaemonContextStub,
                pika_connection = self.pika_connection,
                pika_params = self.parameters,
                application = AdventurerApplicationStub
                )
        app.run()

    
    def test_pika_connection(self):
        '''Connects to rabbitmq'''
        self.assertEquals(self.pika_connection.connection_parameters, self.parameters)

class TestControllerConsumeMessage(unittest.TestCase):

    def test_consumes_messages(self):
        '''Can consume messages'''
        environ = environment.create()
        class DaemonContextStub(object):
            def __init__(spy, pidfile=None):
                pass

            def __enter__(spy):
                return spy

            def __exit__(self, exc_type, exc_value, trackback):
                pass
        self.DaemonContextStub = DaemonContextStub

        class PIDFileStub(object):
            pass
        self.pidfile = PIDFileStub()


        class AdventurerApplicationSpy(object):
            def __call__(spy):
                spy.register_called = False
                return spy

            def register(spy, data):
                spy.register_data = data
        self.AdventurerApplicationSpy = AdventurerApplicationSpy()

        self.pika_connection = fakepika.SelectConnectionFake()
        self.parameters = dict(host='localhost')

        environ = environment.create()
        app = Controller(
                daemonizer = self.DaemonContextStub,
                pika_connection = self.pika_connection,
                pika_params = self.parameters,
                pidfile = self.pidfile,
                application = self.AdventurerApplicationSpy
                )
        app.run()
        
        albert = environ.albert
        albert_json = json.dumps(albert)

        method = frame.Method(1, spec.Basic.ConsumeOk())
        properties = pika.BasicProperties(content_type = 'application/json')
        header = frame.Header(1, len(albert_json), properties)

        self.pika_connection.inject('register', header, albert_json)
        self.pika_connection.trigger_consume('register')

        self.assertEquals(self.AdventurerApplicationSpy.register_data, albert)

if __name__ == '__main__':
    unittest.main()

