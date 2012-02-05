import unittest

from copy import deepcopy

from uuid import uuid4
import json
from datetime import datetime

from tptesting import environment

from trips.service import TripsDb
from tptesting.fakeriak import RiakClientFake, RiakBinary
from tptesting.fakepika import SelectConnectionFake
from bctmessaging.remoting import RemotingClient

class TestTripFixture(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()
        self.riak = RiakClientFake()
        self.bucket_name = 'trips'
        self.bucket = self.riak.bucket(self.bucket_name)

        pika_connection = SelectConnectionFake()
        channel = pika_connection._channel
        rpc_client = RemotingClient(channel)

        self.app = TripsDb(
                rpc_client,
                self.riak, 
                self.bucket_name, 
                'http://test.com',
                )


        self.trip_id = unicode(uuid4())

        ramona = self.environ.ramona
        self.trip = {
            'name': 'Glacier',
            'start': '2012-07-19',
            'end': '2012-07-24',
            'destination': 'Glacier National Park',
            'friends': [
                {'first': ramona.first_name,
                    'last': ramona.last_name,
                    'email': ramona.email,
                    'invite_status': 'accepted'}
                ],
            'gear': dict(),
            'groupgear': list()
            }
        self.bucket.add_document(self.trip_id, self.trip)

        if hasattr(self, 'continueSetUp'):
            self.continueSetUp()

