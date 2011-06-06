import unittest

import pika

from tptesting import environment

from adventurer.injectors import ControllerInjector, ApplicationInjector

class TestInjectorsController(unittest.TestCase):
    def setUp(self):
        class ControllerStub(object):
            def __init__(stub):
                stub.pika_params = None

            def __call__(stub, pika_connection=None, daemonizer=None, pidfile=None,
                    pika_params=None, application=None):
                stub.pika = pika_connection
                stub.daemonizer = daemonizer
                stub.pika_params = pika_params
                stub.application = application

                return stub
        self.appstub = ControllerStub()

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

        class ApplicationStub(object):
            pass
        self.ApplicationStub = ApplicationStub

        class ControllerSUT(ControllerInjector):
            def _ControllerInjector__controller(sut):
                return self.appstub

            def _ControllerInjector__pika_connection(sut):
                return PikaConnectionStub

            def _ControllerInjector__daemoncontext(sut):
                return DaemonContextStub

            def _ControllerInjector__pidfile(sut):
                return self.PIDLockFileSpy

            def _ControllerInjector__application(sut):
                return self.ApplicationStub

        self.app_sut = ControllerSUT()

    def test_controller_creation_pika(self):
        """Controller injector creates the controller with pika"""
        self.app_sut()
        self.assertEquals(self.appstub.pika, self.pikastub)

    def test_controller_creation_daemoncontext(self):
        """Controller injector creates the controller with daemoncontext"""
        self.app_sut()
        self.assertEquals(self.appstub.daemonizer, self.daemoncontextstub)

    def test_injector_returns_controller(self):
        '''The controller() injector should return an controller object'''
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

    def test_application(self):
        '''Test taht the application gets passed in'''
        self.app_sut()
        self.assertEquals(self.appstub.application, self.ApplicationStub)

class TestApplicationInjector(unittest.TestCase):

    def setUp(self):
        class RiakClientSpy(object):
            def __call__(spy):
                return spy

            def bucket(spy, name):
                spy.name = name
                class BucketStub(object):
                    pass
                spy.BucketStub = BucketStub 

                return BucketStub()
        self.RiakClientSpy = RiakClientSpy()

        class ApplicationInjectorSUT(ApplicationInjector):
            def _ApplicationInjector__riak(sut):
                return self.RiakClientSpy

        class PikaChannelStub(object):
            def basic_publish(stub):
                pass
        self.pika_channel = PikaChannelStub()

        sut = ApplicationInjectorSUT()
        self.app = sut()

    def test_creates_riak_dependency(self):
        '''Creates and passes in the dependency on Riak'''
        self.assertTrue(isinstance(self.app.bucket, self.RiakClientSpy.BucketStub))

    def test_uses_adventurers_bucket(self):
        '''Uses the adventurers bucket for the riak dependency'''
        self.assertEquals(self.RiakClientSpy.name, 'adventurers')




if __name__ == '__main__':
    unittest.main()

