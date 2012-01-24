import unittest

import json
import pika
import uuid

from tptesting import thandlers

from trips.route_handler import RouteHandler

KML_DOCUMENT = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"
	xmlns:gx="http://www.google.com/kml/ext/2.2">
  <Document>
    <name>GPS device</name>
    <Snippet>Created Sun Jan 22 12:34:14 2012</Snippet>
<!-- Normal waypoint style -->
    <Style id="waypoint_n">
      <IconStyle>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/pal4/icon61.png</href>
        </Icon>
      </IconStyle>
    </Style>
<!-- Highlighted waypoint style -->
    <Style id="waypoint_h">
      <IconStyle>
        <scale>1.2</scale>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/pal4/icon61.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <StyleMap id="waypoint">
      <Pair>
        <key>normal</key>
        <styleUrl>#waypoint_n</styleUrl>
      </Pair>
      <Pair>
        <key>highlight</key>
        <styleUrl>#waypoint_h</styleUrl>
      </Pair>
    </StyleMap>
    <LookAt>
      <longitude>0.000000</longitude>
      <latitude>0.000000</latitude>
      <range>25642901.611899</range>
    </LookAt>
  </Document>
</kml>'''

class TestRouteHandlerPOST(thandlers.TornadoHandlerTestCase):

    def handler_setup(self):
        self.trip_id = str(uuid.uuid4())

    @property
    def http_headers(self):
        return {
                'Content-Type': 'multipart/form-data',
                }

    def request_handler(self):
        return RouteHandler

    def url(self):
        return '/app/trips/' + self.trip_id + '/map/route'

    def active_user(self):
        return self.environ.ramona.email

    def method(self):
        return 'POST'

    def method_args(self):
        return list([self.trip_id]), dict()

    def file_upload(self):
        return {
                'userfile': [{
                    'filename': 'the_bob.kml',
                    'body': KML_DOCUMENT,
                    'content_type': 'application/vnd.google-earth.kml+xml'
                }]
            }


    def rpc_result(self):
        return ''

    def http_response(self):
        return True

    def expected_rpc_request(self):
        return 'store_route', [self.trip_id, KML_DOCUMENT]

    def expected_durability(self):
        return True

    def remote_service_name(self):
        return 'Trips'

class TestRouteHandlerGET(thandlers.TornadoHandlerTestCase):

    def handler_setup(self):
        self.trip_id = str(uuid.uuid4())

    @property
    def http_content_type(self):
        return 'application/vnd.google-earth.kml+xml'

    def request_handler(self):
        return RouteHandler

    def url(self):
        return '/app/trips/' + self.trip_id + '/map/route'

    def active_user(self):
        return self.environ.ramona.email

    def method(self):
        return 'GET'

    def method_args(self):
        return list([self.trip_id]), dict()

    def rpc_result(self):
        return KML_DOCUMENT

    def http_response(self):
        return self.rpc_result()

    def expected_rpc_request(self):
        return 'get_route', [self.trip_id]

    def expected_durability(self):
        return True

    def remote_service_name(self):
        return 'Trips'

if __name__ == '__main__':
    unittest.main()

