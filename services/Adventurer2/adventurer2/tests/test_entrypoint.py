import unittest

import pika
import uuid
import json

from tptesting import fakepika, spy, fakeriak
from adventurer2.entrypoint import EntryPoint

class TestServiceCreation(unittest.TestCase):

    def setUp(self):
        self.servicespy = spy.SpyObject()
        self.Repository = spy.SpyObject()
        self.riak = fakeriak.RiakClientFake()

        class EntryPointSUT(EntryPoint):
            def _EntryPoint__service(sut):
                return self.servicespy

            def _EntryPoint__repository(sut):
                return self.Repository

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
                    'rpc': 'adventurer_rpc',
                    },
                'database': {
                    'bucket': 'adventurer',
                    'host': 'localhost'
                    }
                }
        self.ep = EntryPointSUT(self.configuration, self.tpenviron)
        self.ep.start()

    def test_creates_service(self):
        '''Creates the gear service'''
        use = spy.UsageRecord('__init__', self.channel, self.configuration,
                self.Repository)
        self.assertTrue(self.servicespy.verify_usage(use))

    def test_calls_start(self):
        '''Calls the AdventurerService.start() method'''
        self.assertTrue(self.servicespy.was_called('start'))

    def test_repository_created(self):
        '''Creates the repository'''
        use = spy.UsageRecord('__init__', self.riak,
                self.configuration['database']['bucket'])
        self.assertTrue(self.Repository.verify_usage(use))

    def test_riakclient(self):
        '''Creates the riak client'''
        self.assertEquals(self.configuration['database']['host'], self.riak.host)

        



if __name__ == '__main__':
    unittest.main()
