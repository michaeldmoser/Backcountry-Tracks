import unittest

import pika
import uuid
import json

from tptesting import fakepika, spy, fakeriak
from trips.entrypoint import EntryPoint

class TestServiceCreation(unittest.TestCase):

    def setUp(self):
        self.servicespy = spy.SpyObject()
        self.TripsDbStub = spy.SpyObject()

        self.riak = fakeriak.RiakClientFake()

        class EntryPointSUT(EntryPoint):
            def _EntryPoint__service(sut):
                return self.servicespy

            def _EntryPoint__db(sut):
                return self.TripsDbStub

            def _EntryPoint__riak(sut):
                return self.riak

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
                self.TripsDbStub)
        self.assertTrue(self.servicespy.verify_usage(use))

    def test_calls_start(self):
        '''Calls the TripsService.start() method'''
        self.assertTrue(self.servicespy.was_called('start'))

    def test_tripsdb_created(self):
        '''Creates the trips db'''
        use = spy.UsageRecord('__init__', self.riak,
                self.configuration['database']['bucket'])
        self.assertTrue(self.TripsDbStub.verify_usage(use))

    def test_riakclient(self):
        '''Creates the riak client'''
        self.assertEquals(self.configuration['database']['host'], self.riak.host)

        



if __name__ == '__main__':
    unittest.main()

