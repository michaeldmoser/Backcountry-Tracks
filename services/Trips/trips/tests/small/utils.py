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

from bctks_glbldb import Connection

class TestTripFixture(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()
        self.riak = RiakClientFake()
        self.bucket_name = 'trips'
        self.bucket = self.riak.bucket(self.bucket_name)

        pika_connection = SelectConnectionFake()
        channel = pika_connection._channel
        self.channel = channel
        rpc_client = RemotingClient(channel)
        dbcon = Connection(self.riak)

        self.app = TripsDb(
                rpc_client,
                self.riak, 
                self.bucket_name, 
                'http://test.com',
                db=dbcon
                )


        self.trip_id = unicode(uuid4())

        ramona = self.environ.ramona
        douglas = self.environ.douglas
        albert = self.environ.albert
        self.trip = {
            'name': 'Glacier',
            'start': '2012-07-19',
            'end': '2012-07-24',
            'destination': 'Glacier National Park',
            'owner': douglas.email,
            'friends': [
                {'first': ramona.first_name,
                    'last': ramona.last_name,
                    'email': ramona.email,
                    'invite_status': 'accepted'},
                {'first': douglas.first_name,
                    'last': douglas.last_name,
                    'email': douglas.email,
                    'invite_status': 'accepted',
                    },
                {'first': albert.first_name,
                    'last': albert.last_name,
                    'email': albert.email,
                    'invite_status': 'rejected',
                    }
                ],
            'gear': dict(),
            'groupgear': list()
            }
        self.bucket.add_document(self.trip_id, self.trip)

        if hasattr(self, 'continueSetUp'):
            self.continueSetUp()

