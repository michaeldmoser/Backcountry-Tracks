import unittest

import pika

from tptesting import environment

from adventurer.injectors import ApplicationInjector

class TestInjectorsApplication(unittest.TestCase):
    def setUp(self):
        class ApplicationStub(object):
            def __init__(stub):
                stub.pika_params = None

            def __call__(stub, pika_connection=None, daemonizer=None, pidfile=None,
                    pika_params=None):
                stub.pika = pika_connection
                stub.daemonizer = daemonizer
                stub.pika_params = pika_params

                return stub
        self.appstub = ApplicationStub()

        class PikaConnectionStub(object):
            pass
        self.pikastub = PikaConnectionStub

        class DaemonContextStub(object):
            pass
        self.daemoncontextstub = DaemonContextStub

        class PIDLockFileSpy(object):
            def __init__(spy):
                spy.pidfile = None

            def __call__(spy, pidfile_path):
                spy.pidfile = pidfile_path
        self.PIDLockFileSpy = PIDLockFileSpy()

        class ApplicationSUT(ApplicationInjector):
            def _ApplicationInjector__application(sut):
                return self.appstub

            def _ApplicationInjector__pika_connection(sut):
                return PikaConnectionStub

            def _ApplicationInjector__daemoncontext(sut):
                return DaemonContextStub

            def _ApplicationInjector__pidfile(sut):
                return self.PIDLockFileSpy

        self.app_sut = ApplicationSUT()

    def test_application_creation_pika(self):
        """Application injector creates the application with pika"""
        self.app_sut()
        self.assertEquals(self.appstub.pika, self.pikastub)

    def test_application_creation_daemoncontext(self):
        """Application injector creates the application with daemoncontext"""
        self.app_sut()
        self.assertEquals(self.appstub.daemonizer, self.daemoncontextstub)

    def test_injector_returns_application(self):
        '''The application() injector should return an application object'''
        app = self.app_sut()
        self.assertTrue(isinstance(app, self.appstub.__class__))

    def test_pidfile(self):
        '''PID lock file gets created with correct path'''
        self.app_sut()
        environ = environment.create()
        pidfile_path = environ.get_config_for('adventurer')['pidfile']
        self.assertEquals(self.PIDLockFileSpy.pidfile, pidfile_path)

    def test_pika_params(self):
        '''Paramenters for the pika connection get passed in'''
        self.app_sut()
        parameters = pika.ConnectionParameters(host = 'localhost')
        self.assertEquals(self.appstub.pika_params.host, parameters.host)

if __name__ == '__main__':
    unittest.main()
