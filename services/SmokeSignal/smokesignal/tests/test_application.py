import unittest

from smokesignal.application import SmokeSignalApp

class TestSmokeSignalApp(unittest.TestCase):
    def test_accepts_pika_connection(self):
        """Should take a pika connection"""
        class PikaConnectionStub(object):
            pass

        app = SmokeSignalApp(pika_connection = PikaConnectionStub())

    def test_creates_exchange(self):
        '''Creates the registration exchange'''
        class ChannelSpy(object):
            def exchange_declare(spy, callback=None, ticket=0, exchange=None, 
                    type='direct', passive=False, durable=False, auto_delete=False,
                    internal=False, nowait=False, arguments={}):
                spy.args = {
                        'exchange': exchange,
                        'type': type,
                        'durable': durable,
                        'auto_delete': auto_delete,
                        'internal': internal,
                        'arguments': arguments
                        }

            def queue_bind(spy, callback=None, ticket=0, queue='', exchange=None,
                    routing_key='', nowait=False, arguments={}):
                pass

            def queue_declare(spy, callback=None, ticket=0, queue='', 
                    passive=False, durable=False, exclusive=False, auto_delete=False,
                    nowait=False, arguments={}):
                pass
        channelspy = ChannelSpy()

        class PikaConnectionStub(object):
            def channel(stub):
                return channelspy

        app = SmokeSignalApp(PikaConnectionStub())
        app.run()

        expected_exchange_declare = {
            'exchange': 'registration',
            'type': 'topic',
            'durable': True,
            'auto_delete': False,
            'internal': False,
            'arguments': {}
            }
        self.assertEquals(expected_exchange_declare, channelspy.args)

    def test_creates_queue(self):
        '''Creates the register queue'''
        class ChannelSpy(object):
            def exchange_declare(spy, callback=None, ticket=0, exchange=None, 
                    type='direct', passive=False, durable=False, auto_delete=False,
                    internal=False, nowait=False, arguments={}):
                pass

            def queue_bind(spy, callback=None, ticket=0, queue='', exchange=None,
                    routing_key='', nowait=False, arguments={}):
                pass

            def queue_declare(spy, callback=None, ticket=0, queue='', 
                    passive=False, durable=False, exclusive=False, auto_delete=False,
                    nowait=False, arguments={}):
                spy.args = {
                        'queue': queue,
                        'durable': durable,
                        'auto_delete': auto_delete,
                        'arguments': arguments
                        }
        channelspy = ChannelSpy()

        class PikaConnectionStub(object):
            def channel(stub):
                return channelspy

        app = SmokeSignalApp(PikaConnectionStub())
        app.run()

        expected_queue_declare = {
            'queue': 'register',
            'durable': True,
            'auto_delete': False,
            'arguments': {}
            }
        self.assertEquals(expected_queue_declare, channelspy.args)

    def test_creates_binding(self):
        '''Creates the exchange<->queue binding'''
        class ChannelSpy(object):
            def exchange_declare(spy, callback=None, ticket=0, exchange=None, 
                    type='direct', passive=False, durable=False, auto_delete=False,
                    internal=False, nowait=False, arguments={}):
                pass

            def queue_declare(spy, callback=None, ticket=0, queue='', 
                    passive=False, durable=False, exclusive=False, auto_delete=False,
                    nowait=False, arguments={}):
                pass

            def queue_bind(spy, callback=None, ticket=0, queue='', exchange=None,
                    routing_key='', nowait=False, arguments={}):
                spy.args = {
                        'queue': queue,
                        'exchange': exchange,
                        'routing_key': routing_key,
                        'arguments': arguments
                        }
        channelspy = ChannelSpy()

        class PikaConnectionStub(object):
            def channel(stub):
                return channelspy

        app = SmokeSignalApp(PikaConnectionStub())
        app.run()

        expected_binding = {
            'queue': 'register',
            'exchange': 'registration',
            'routing_key': 'registration.register',
            'arguments': {}
            }
        self.assertEquals(expected_binding, channelspy.args)

if __name__ == '__main__':
    unittest.main()
