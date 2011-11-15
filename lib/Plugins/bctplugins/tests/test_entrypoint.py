import unittest

import pika
import uuid
import json

from tptesting import fakepika, spy, fakeriak
from bctplugins.entrypoint import EntryPoint, MessagingEntryPointFactory

class TestServiceCreation(unittest.TestCase):

    def setUp(self):
        self.controllerspy = spy.SpyObject()
        self.ServiceStub = spy.SpyObject()

        self.riak = fakeriak.RiakClientFake()

        class EntryPointSUT(EntryPoint):
            controller = self.controllerspy
            service = self.ServiceStub
            database = self.riak

        mq = fakepika.SelectConnectionFake()
        mq.ioloop.start()
        self.channel = mq._channel

        class EnvironmentStub(object):
            def open_messaging_channel(stub, on_channel_callback):
                on_channel_callback(self.channel)
        self.tpenviron = EnvironmentStub()

        self.configuration = {
                'queues': {
                    'rpc': 'trips_rpc'
                    },
                'database': {
                    'bucket': 'trips',
                    'host': 'localhost'
                    }
                }
        tripsep = EntryPointSUT(self.configuration, self.tpenviron)
        tripsep.start()

    def test_creates_service(self):
        '''Creates the trips service'''
        use = spy.UsageRecord('__init__', self.channel, self.configuration,
                self.ServiceStub)
        self.assertTrue(self.controllerspy.verify_usage(use))

    def test_calls_start(self):
        '''Calls the TripsService.start() method'''
        self.assertTrue(self.controllerspy.was_called('start'))

    def test_tripsdb_created(self):
        '''Creates the trips db'''
        use = spy.UsageRecord('__init__', self.riak,
                self.configuration['database']['bucket'])
        self.assertTrue(self.ServiceStub.verify_usage(use))

    def test_riakclient(self):
        '''Creates the riak client'''
        self.assertEquals(self.configuration['database']['host'], self.riak.host)

class TestMessagingEntryPointFactory(unittest.TestCase):

    def setUp(self):
        self.controllerspy = spy.SpyObject()
        self.ServiceStub = spy.SpyObject()


        class EntryPointSUT(MessagingEntryPointFactory):
            def assemble_controller(sut):
                return self.controllerspy

            def assemble_service(sut):
                return self.ServiceStub

        mq = fakepika.SelectConnectionFake()
        mq.ioloop.start()
        self.channel = mq._channel

        class EnvironmentStub(object):
            def open_messaging_channel(stub, on_channel_callback):
                on_channel_callback(self.channel)
        self.tpenviron = EnvironmentStub()

        self.configuration = {
                'queues': {
                    'rpc': 'trips_rpc'
                    },
                'database': {
                    'bucket': 'trips',
                    'host': 'localhost'
                    }
                }
        tripsep = EntryPointSUT(self.configuration, self.tpenviron)
        tripsep.start()

    def test_creates_service(self):
        '''Creates the trips service'''
        use = spy.UsageRecord('__init__', self.channel, self.configuration,
                self.ServiceStub)
        self.assertTrue(self.controllerspy.verify_usage(use))

    def test_calls_start(self):
        '''Calls the TripsService.start() method'''
        self.assertTrue(self.controllerspy.was_called('start'))


if __name__ == '__main__':
    unittest.main()

