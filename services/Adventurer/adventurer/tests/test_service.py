import unittest

import json
from pika import frame, spec
import pika

from tptesting import environment

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

        class PikaConnectionStub(object):
            def __init__(self, parameters, on_open_callback=None):
                class ioloop(object):
                    def start(ioloopself):
                        pass
                self.ioloop = ioloop()

        class AdventurerApplicationStub(object):
            def register(spy, data):
                pass

        self.daemonizer = self.DaemonContextSpy()
        app = Controller(
                daemonizer = self.daemonizer,
                pidfile = self.pidfile,
                pika_params = dict(),
                pika_connection = PikaConnectionStub,
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

        class PikaConnectionSpy(object):
            def __call__(spy, parameters, on_open_callback=None):
                spy.ioloop_started = False
                class ioloop(object):
                    def start(ioloopself):
                        spy.ioloop_started = True
                spy.ioloop = ioloop()

                spy.parameters = parameters
                spy.on_open_callback = on_open_callback
                on_open_callback(spy)

                return spy

            def channel(spy, callback=None):
                spy.channel_callback = callback
                class PikaChannelSpy(object):
                    def basic_consume(channelspy, callback, queue=None):
                        spy.consume_callback = callback
                        spy.queue = queue
                callback(PikaChannelSpy())

        self.pika_connection = PikaConnectionSpy()
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
        self.assertEquals(self.pika_connection.parameters, self.parameters)

    def test_opens_channel(self):
        '''Creates a channel on the Pika connection'''
        self.assertTrue(hasattr(self.pika_connection, 'channel_callback'), 'No channel was opened')

    def test_consumes_messages(self):
        '''Starts consuming messages'''
        expected_consume = {
                'queue': 'registrations',
                'callback': True
                }
        actual_consume = {
                'queue': self.pika_connection.queue,
                'callback': self.pika_connection.consume_callback is not None
                }
        self.assertEquals(actual_consume, expected_consume)

    def test_ioloop_started(self):
        '''The ioloop should be started'''
        self.assertTrue(self.pika_connection.ioloop_started)

class TestControllerConsumeMessage(unittest.TestCase):

    def test_consumes_messages(self):
        '''Can consume messages'''
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

        class PikaConnectionSpy(object):
            def __call__(spy, parameters, on_open_callback=None):
                spy.ioloop_started = False
                class ioloop(object):
                    def start(ioloopself):
                        pass
                spy.ioloop = ioloop()
                on_open_callback(spy)

                return spy

            def channel(spy, callback=None):
                class PikaChannelSpy(object):
                    def basic_consume(channelspy, callback, queue=None):
                        spy.consume_callback = callback
                spy.channel = PikaChannelSpy()
                callback(spy.channel)
        self.pika_connection = PikaConnectionSpy()
        self.parameters = dict(host='localhost')

        class AdventurerApplicationSpy(object):
            def __call__(spy):
                spy.register_called = False
                return spy

            def register(spy, data):
                spy.register_data = data
        self.AdventurerApplicationSpy = AdventurerApplicationSpy()

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

        delivery_callback = self.pika_connection.consume_callback
        delivery_callback(self.pika_connection.channel, method, header, albert_json)

        self.assertEquals(self.AdventurerApplicationSpy.register_data, albert)

if __name__ == '__main__':
    unittest.main()

