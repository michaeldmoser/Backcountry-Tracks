import unittest

import pika
import uuid
import json

from tptesting import fakepika
from gear.service import GearService

class TestReturnsListOfGear(unittest.TestCase):

    def setUp(self):
        self.list_of_gear = [
                        {'name': 'Backpack', 'description': '', 'weight': '48'},
                        {'name': 'Stove', 'description': '', 'weight': '16'},
                        {'name': 'Tarp', 'description': '', 'weight': '26'},
                        ]
        class GearDbStub(object):
            def list(stub, user):
                return self.list_of_gear 

        mq = fakepika.SelectConnectionFake()
        mq.ioloop.start()
        channel = mq._channel # Is this cheating? Should we make it not cheating?

        configuration = {
                'queues': {
                    'user_gear': 'gear_user_rpc'
                    }
                }

        gearep = GearService(channel, configuration, GearDbStub())
        gearep.start()

        self.properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = str(uuid.uuid4()),
                reply_to = str(uuid.uuid4())
                )
        request = {
                'jsonrpc': '2.0',
                'method': 'list',
                'params': ['bob@smith.com'],
                'id': self.properties.correlation_id,
                }
        mq.inject('gear_user_rpc', self.properties, json.dumps(request))
        mq.trigger_consume('gear_user_rpc')

        self.reply = mq.published_messages[0]

    def test_send_list_of_gear(self):
        '''Should respond to RPC message with list of returned gear'''
        gear_list = json.loads(self.reply.body)
        self.assertEquals(self.list_of_gear, gear_list)

    def test_sent_to_exchange(self):
        '''Response message gets sent to rpc_reply exchange'''
        exchange = self.reply.exchange
        self.assertEquals('rpc_reply', exchange)

    def test_routing_key(self):
        '''Response sent to correct routing_key'''
        routing_key = self.reply.routing_key
        self.assertEquals(self.properties.reply_to, routing_key)

    def test_content_type(self):
        '''Respone content type is json'''
        content_type = self.reply.properties.content_type
        self.assertEquals('application/json', content_type)

    def test_correlation_id(self):
        '''Response has correct correlation id'''
        correlation_id = self.reply.properties.correlation_id
        self.assertEquals(self.properties.correlation_id, correlation_id)

    def test_delivery_mode(self):
        '''Does not need to be a persisted message'''
        delivery_mode = self.reply.properties.delivery_mode
        self.assertIsNone(delivery_mode)


class TestCreateGear(unittest.TestCase):

    def setUp(self):
        user = 'bob@smith.com'
        new_gear = {
                'name': 'Backpack',
                'description': '',
                'weight': '48'
                }
        self.gear_return = new_gear.copy()
        self.gear_return.update({'id': str(uuid.uuid4()), 'owner': user})

        class GearDbStub(object):
            def create(stub, user, pieceofgear):
                return self.gear_return

        mq = fakepika.SelectConnectionFake()
        mq.ioloop.start()
        channel = mq._channel # Is this cheating? Should we make it not cheating?

        configuration = {
                'queues': {
                    'user_gear': 'gear_user_rpc'
                    }
                }

        gearep = GearService(channel, configuration, GearDbStub())
        gearep.start()

        self.properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = str(uuid.uuid4()),
                reply_to = str(uuid.uuid4())
                )
        request = {
                'jsonrpc': '2.0',
                'method': 'create',
                'params': [user, new_gear],
                'id': self.properties.correlation_id,
                }
        mq.inject('gear_user_rpc', self.properties, json.dumps(request))
        mq.trigger_consume('gear_user_rpc')

        self.reply = mq.published_messages[0]

    def test_reply(self):
        body = json.loads(self.reply.body)
        self.assertEquals(body, self.gear_return)

class TestUpdateGear(unittest.TestCase):

    def setUp(self):
        user = 'bob@smith.com'
        new_gear = {
                'name': 'Backpack',
                'description': '',
                'weight': '48',
                'id': str(uuid.uuid4()),
                'owner': user,
                }
        self.gear_return = new_gear.copy()

        class GearDbStub(object):
            def update(stub, user, gear_id, pieceofgear):
                return self.gear_return

        mq = fakepika.SelectConnectionFake()
        mq.ioloop.start()
        channel = mq._channel # Is this cheating? Should we make it not cheating?

        configuration = {
                'queues': {
                    'user_gear': 'gear_user_rpc'
                    }
                }

        gearep = GearService(channel, configuration, GearDbStub())
        gearep.start()

        self.properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = str(uuid.uuid4()),
                reply_to = str(uuid.uuid4())
                )
        request = {
                'jsonrpc': '2.0',
                'method': 'update',
                'params': [user, new_gear['id'], new_gear],
                'id': self.properties.correlation_id,
                }
        mq.inject('gear_user_rpc', self.properties, json.dumps(request))
        mq.trigger_consume('gear_user_rpc')

        self.reply = mq.published_messages[0]

    def test_reply(self):
        body = json.loads(self.reply.body)
        self.assertEquals(body, self.gear_return)


class TestDeleteGear(unittest.TestCase):

    def setUp(self):
        user = 'bob@smith.com'
        new_gear = {
                'name': 'Backpack',
                'description': '',
                'weight': '48',
                'id': str(uuid.uuid4()),
                'owner': user,
                }
        self.gear_return = new_gear.copy()

        class GearDbStub(object):
            def delete(stub, user, gear_id):
                pass

        mq = fakepika.SelectConnectionFake()
        mq.ioloop.start()
        channel = mq._channel # Is this cheating? Should we make it not cheating?

        configuration = {
                'queues': {
                    'user_gear': 'gear_user_rpc'
                    }
                }

        gearep = GearService(channel, configuration, GearDbStub())
        gearep.start()

        self.properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = str(uuid.uuid4()),
                reply_to = str(uuid.uuid4())
                )
        request = {
                'jsonrpc': '2.0',
                'method': 'delete',
                'params': [user, new_gear['id']],
                'id': self.properties.correlation_id,
                }
        mq.inject('gear_user_rpc', self.properties, json.dumps(request))
        mq.trigger_consume('gear_user_rpc')

        self.reply = mq.published_messages

    def test_reply(self):
        self.assertEquals(len(self.reply), 0)


if __name__ == '__main__':
    unittest.main()


