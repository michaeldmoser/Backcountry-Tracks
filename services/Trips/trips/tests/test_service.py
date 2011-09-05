import unittest

import pika
import uuid
import json

from tptesting import fakepika, environment
from trips.service import TripsService

class TestCreateTrip(unittest.TestCase):

    def setUp(self):
        environ = environment.create()
        user = 'bob@smith.com'
        new_trip = environ.data['trips'][0] 

        self.trip_return = new_trip.copy()
        self.trip_return.update({'id': str(uuid.uuid4()), 'owner': user})

        class TripsDbStub(object):
            def create(stub, user, trip):
                return self.trip_return

        mq = fakepika.SelectConnectionFake()
        mq.ioloop.start()
        channel = mq._channel # Is this cheating? Should we make it not cheating?

        queue_name = 'trips_rpc'
        config = {
                'queues': {
                    'rpc': queue_name
                    }
                }

        gearep = TripsService(channel, config, TripsDbStub())
        gearep.start()

        self.properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = str(uuid.uuid4()),
                reply_to = str(uuid.uuid4())
                )
        request = {
                'jsonrpc': '2.0',
                'method': 'create',
                'params': [user, new_trip],
                'id': self.properties.correlation_id,
                }
        mq.inject(queue_name, self.properties, json.dumps(request))
        mq.trigger_consume(queue_name)

        self.reply = mq.published_messages[0]

    def test_reply(self):
        body = json.loads(self.reply.body)
        self.assertEquals(body, self.trip_return)

class TestUpdateTrip(unittest.TestCase):

    def setUp(self):
        environ = environment.create()
        user = 'bob@smith.com'
        new_trip = environ.data['trips'][0].copy()
        new_trip.update({
            'owner': user,
            'id': str(uuid.uuid4())
            })

        self.trip_return = new_trip.copy()

        class TripsDbStub(object):
            def update(stub, user, trip_id, trip):
                return self.trip_return

        mq = fakepika.SelectConnectionFake()
        mq.ioloop.start()
        channel = mq._channel # Is this cheating? Should we make it not cheating?

        queue_name = 'trips_rpc'
        config = {
                'queues': {
                    'rpc': queue_name
                    }
                }

        gearep = TripsService(channel, config, TripsDbStub())
        gearep.start()

        self.properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = str(uuid.uuid4()),
                reply_to = str(uuid.uuid4())
                )
        request = {
                'jsonrpc': '2.0',
                'method': 'update',
                'params': [user, new_trip['id'], new_trip],
                'id': self.properties.correlation_id,
                }
        mq.inject(queue_name, self.properties, json.dumps(request))
        mq.trigger_consume(queue_name)

        self.reply = mq.published_messages[0]

    def test_reply(self):
        body = json.loads(self.reply.body)
        self.assertEquals(body, self.trip_return)

if __name__ == '__main__':
    unittest.main()


