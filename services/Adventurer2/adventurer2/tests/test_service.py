import unittest

import pika
import uuid
import json

from tptesting import fakepika, environment

from adventurer2.service import AdventurerService

class TestAdventurer2Service(unittest.TestCase):
    def setUp(self):
        self.environ = environment.create()

        class AdventurerRepositoryFake(object):
            def get(fake, user):
                if user != self.environ.douglas.email:
                    return None
                return dict(self.environ.douglas)

        mq = fakepika.SelectConnectionFake()
        mq.ioloop.start()
        channel = mq._channel # Is this cheating? Should we make it not cheating?

        rpc_queue = 'adventurer_rpc'
        configuration = {
                'queues': {
                    'rpc': rpc_queue
                    }
                }

        adventurer_service = AdventurerService(channel, configuration, AdventurerRepositoryFake())
        adventurer_service.start()

        self.properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = str(uuid.uuid4()),
                reply_to = str(uuid.uuid4())
                )
        request = {
                'jsonrpc': '2.0',
                'method': 'get',
                'params': [self.environ.douglas.email],
                'id': self.properties.correlation_id,
                }
        mq.inject(rpc_queue, self.properties, json.dumps(request))
        mq.trigger_consume(rpc_queue)

        self.reply = mq.published_messages[0]

    def test_send_user_data(self):
        '''Should respond to RPC message with user data'''
        user_data = json.loads(self.reply.body)
        self.assertEquals(self.environ.douglas, user_data)

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


if __name__ == '__main__':
    unittest.main()

