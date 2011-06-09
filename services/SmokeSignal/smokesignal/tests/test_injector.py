import unittest

from smokesignal.injector import SmokeSignalFactory

class TestSmokeSignalFactory(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pika_connection(self):
        """Creates a pika connection"""
        class PikaBlockConnectionStub(object):
            def __init__(self, parameters):
                pass

        class SmokeSignalAppSpy(object):
            def __call__(spy, pika_connection=None):
                spy.pika_connection = pika_connection
        application = SmokeSignalAppSpy()

        class SmokeSignalFactorySpy(SmokeSignalFactory):
            def _SmokeSignalFactory__application(spy):
                return application

            def _SmokeSignalFactory__pika_connection(spy):
                return PikaBlockConnectionStub

            def _SmokeSignalFactory__subprocess(sut):
                def call(command, stdin=None, stdout=None):
                    pass
                return call

        factory = SmokeSignalFactorySpy()
        app = factory()

        self.assertIsInstance(application.pika_connection, PikaBlockConnectionStub)

    def test_pika_connection_params(self):
        '''Parameters to pika connection are correct'''
        class PikaBlockingConnectionSpy(object):
            def __call__(self, parameters):
                self.parameters = parameters
        connectionspy = PikaBlockingConnectionSpy()

        class SmokeSignalAppStub(object):
            def __init__(stub, pika_connection=None):
                pass

        class SmokeSignalFactorySUT(SmokeSignalFactory):
            def _SmokeSignalFactory__application(sut):
                return SmokeSignalAppStub 

            def _SmokeSignalFactory__pika_connection(sut):
                return connectionspy

            def _SmokeSignalFactory__subprocess(sut):
                def call(command, stdin=None, stdout=None):
                    pass
                return call
        factory = SmokeSignalFactorySUT()
        app = factory()

        self.assertEquals('localhost', connectionspy.parameters.host)

    def test_starts_rabbitmq(self):
        '''Needs to start the rabbitmq server'''
        class PikaBlockConnectionStub(object):
            def __init__(self, parameters):
                pass

        class SmokeSignalAppStub(object):
            def __init__(stub, pika_connection=None):
                pass

        class SubprocessSpy(object):
            def call(spy, command, stdin=None, stdout=None):
                spy.command = command
        subprocesspy = SubprocessSpy()


        class SmokeSignalFactorySUT(SmokeSignalFactory):
            def _SmokeSignalFactory__application(sut):
                return SmokeSignalAppStub 

            def _SmokeSignalFactory__pika_connection(sut):
                return PikaBlockConnectionStub

            def _SmokeSignalFactory__subprocess(sut):
                return subprocesspy.call

        factory = SmokeSignalFactorySUT()
        app = factory()

        expected_command = ['/etc/init.d/rabbitmq-server', 'start']
        actual_command = subprocesspy.command
        self.assertEquals(expected_command, actual_command)


if __name__ == '__main__':
    unittest.main()
