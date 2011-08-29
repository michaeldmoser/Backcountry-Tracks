import unittest

import pika
import uuid
import json

from tptesting import fakepika, spy, fakeriak
from gear.entrypoint import GearEntryPoint

class TestServiceCreation(unittest.TestCase):

    def setUp(self):
        self.servicespy = spy.SpyObject()
        self.UserGearStub = spy.SpyObject()

        self.riak = fakeriak.RiakClientFake()

        class GearEntryPointSUT(GearEntryPoint):
            def _GearEntryPoint__gearservice(sut):
                return self.servicespy

            def _GearEntryPoint__usergear(sut):
                return self.UserGearStub

            def _GearEntryPoint__riak(sut):
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
                    'user_gear': 'gear_user_rpc'
                    },
                'database': {
                    'bucket': 'gear',
                    'host': 'localhost'
                    }
                }
        self.gearep = GearEntryPointSUT(self.configuration, self.tpenviron)
        self.gearep.start()

    def test_creates_service(self):
        '''Creates the gear service'''
        use = spy.UsageRecord('__init__', self.channel, self.configuration,
                self.UserGearStub)
        self.assertTrue(self.servicespy.verify_usage(use))

    def test_calls_start(self):
        '''Calls the GearService.start() method'''
        self.assertTrue(self.servicespy.was_called('start'))

    def test_usergear_created(self):
        '''Creates the user gear db'''
        use = spy.UsageRecord('__init__', self.riak,
                self.configuration['database']['bucket'])
        self.assertTrue(self.UserGearStub.verify_usage(use))

    def test_riakclient(self):
        '''Creates the riak client'''
        self.assertEquals(self.configuration['database']['host'], self.riak.host)

        



if __name__ == '__main__':
    unittest.main()

