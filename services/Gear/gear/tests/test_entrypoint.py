import unittest

import pika
import uuid
import json

from tptesting import fakepika
from gear.entrypoint import GearEntryPoint

class TestServiceCreation(unittest.TestCase):

    def setUp(self):
        class GearServiceSpy(object):
            def __call__(spy, channel, config, usergear):
                spy.geardb = usergear
                spy.channel = channel
                spy.config = config
                spy.start_called = False

                return spy

            def start(spy):
                spy.start_called = True
        self.servicespy = GearServiceSpy()

        class UserGearStub(object):
            pass
        self.UserGearStub = UserGearStub

        class GearEntryPointSUT(GearEntryPoint):
            def _GearEntryPoint__gearservice(sut):
                return self.servicespy

            def _GearEntryPoint__usergear(sut):
                return UserGearStub

        mq = fakepika.SelectConnectionFake()
        mq.ioloop.start()
        self.channel = mq._channel

        self.configuration = {
                'queues': {
                    'user_gear': 'gear_user_rpc'
                    }
                }
        self.gearep = GearEntryPointSUT(self.channel, self.configuration)

    def test_creates_service_with_config(self):
        '''Uses correct config when creating service'''
        self.assertEquals(self.configuration, self.servicespy.config)

    def test_creates_service_with_channel(self):
        '''Uses correct channel when creating service'''
        self.assertEquals(self.channel, self.servicespy.channel)

    def test_usergear_passed_in(self):
        '''Passes in an UserGear instance'''
        self.assertIsInstance(self.servicespy.geardb, self.UserGearStub)

    def test_calls_start(self):
        '''Calls the GearService.start() method'''
        self.gearep.start()
        self.assertTrue(self.servicespy.start_called)


if __name__ == '__main__':
    unittest.main()

