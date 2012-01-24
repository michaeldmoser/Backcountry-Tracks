import unittest

from copy import deepcopy

from uuid import uuid4
import json

from tptesting import environment

from trips.service import TripsDb
from tptesting.fakeriak import RiakClientFake, RiakBinary
from tptesting.fakepika import SelectConnectionFake
from bctmessaging.remoting import RemotingClient

from trips.tests.test_route_handler import KML_DOCUMENT
KML_DOCUMENT = unicode(KML_DOCUMENT)
GPX_DOCUMENT = unicode('''<?xml version="1.0" encoding="UTF-8"?>
<gpx
  version="1.0"
  creator="GPSBabel - http://www.gpsbabel.org"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns="http://www.topografix.com/GPX/1/0"
  xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">
<time>2012-01-22T18:33:30Z</time>
</gpx>''')

class GPSFileConverterFake(object):
    def __init__(self, document):
        pass

    def convert(self, to_format):
        return KML_DOCUMENT

class TestTripStoreRoute(unittest.TestCase):

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
                converter = GPSFileConverterFake
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



    def test_store_kml_route(self):
        '''Should store kml data for a route'''
        gear = self.app.store_route(self.trip_id, KML_DOCUMENT)

        tripobj = self.bucket.get(str(self.trip_id))
        trip = tripobj.get_data()
        route = trip.get('route', '')

        self.assertIn(route, KML_DOCUMENT)

class TestTripRetrieveRoute(unittest.TestCase):

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
                self.riak, self.bucket_name, 'http://test.com'
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
            'groupgear': list(),
            }
        self.bucket.add_document(self.trip_id, self.trip)

        document = self.bucket.get(str(self.trip_id))

        route_bucket = self.riak.bucket('maps')
        route_id = str(uuid4())
        routeobj = route_bucket.new_binary(route_id, str(KML_DOCUMENT),
                content_type='vnd.google-earth.kml+xml')
        route_bucket.documents[route_id] = RiakBinary(KML_DOCUMENT)

        document.add_link(routeobj, tag='route')
        document.store()

    def test_get_kml_route(self):
        '''Should get a kml document for route'''
        route = self.app.get_route(self.trip_id)
        self.assertEquals(route, KML_DOCUMENT)

class TestTripStoreGPXRoute(unittest.TestCase):

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
                converter = GPSFileConverterFake
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

    def test_store_kml_route(self):
        '''Storing a GPX document should save as a KML document'''
        gear = self.app.store_route(self.trip_id, GPX_DOCUMENT)

        tripobj = self.bucket.get(str(self.trip_id))
        trip = tripobj.get_data()
        route = trip.get('route', '')

        self.assertIn(route, KML_DOCUMENT)

if __name__ == '__main__':
    unittest.main()

