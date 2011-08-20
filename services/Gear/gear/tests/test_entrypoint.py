import unittest

import pika
import uuid
import json

from tptesting import fakepika, spy
from gear.entrypoint import GearEntryPoint

class TestServiceCreation(unittest.TestCase):

    def setUp(self):
        self.servicespy = spy.SpyObject()

        class UserGearStub(object):
            def __call__(self):
                return self
        self.UserGearStub = UserGearStub()

        class GearEntryPointSUT(GearEntryPoint):
            def _GearEntryPoint__gearservice(sut):
                return self.servicespy

            def _GearEntryPoint__usergear(sut):
                return self.UserGearStub

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
                    }
                }
        self.gearep = GearEntryPointSUT(self.tpenviron, self.configuration)
        self.gearep.start()

    def test_creates_service(self):
        '''Creates the gear service'''
        use = spy.UsageRecord('__init__', self.channel, self.configuration,
                self.UserGearStub)
        self.assertTrue(self.servicespy.verify_usage(use))

    def test_calls_start(self):
        '''Calls the GearService.start() method'''
        self.assertTrue(self.servicespy.was_called('start'))


if __name__ == '__main__':
    unittest.main()

