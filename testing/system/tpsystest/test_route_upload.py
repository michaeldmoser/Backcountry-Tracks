import unittest
import urllib2
import json
import pika
import os.path

from urllib2 import HTTPError


from tptesting import environment, utils

from bctmessaging.remoting import RemoteService

class TestRouteUpload(unittest.TestCase):

    def create_upload_request(self, filename):
        headers = {
                'Content-Type': 'multipart/form-data; boundary=formboundary'
                }

        dir_path = os.path.dirname(__file__)
        kml_path = os.path.join(dir_path, filename)
        kml_data = open(kml_path, 'r').read()
        
        post_body_lines = [
                '--formboundary',
                'Content-Disposition: form-data; name="userfile"; filename=%s' % filename,
                'Content-Type: application/vnd.google-earth.kml+xml',
                '',
                kml_data,
                '',
                '--formboundary--'
                ]
        post_body = '\r\n'.join(post_body_lines)
        headers['Content-Length'] = len(post_body)

        route_request = urllib2.Request(
                self.url,
                data=post_body,
                headers=headers
               ) 
        return route_request, kml_data

    def setUp(cls):
        env = environment.create()
        env.make_pristine()
        env.bringup_infrastructure()

        douglas = env.douglas
        env.create_user(douglas)
        login_session = douglas.login()

        trips = env.trips.add_trips_to_user(douglas, env.data['trips'])
        trip = trips[0]

        url = env.trailhead_url + '/trips/%s/map/route' % trip['id']
        cls.url = url


        route_request, kml_data = cls.create_upload_request('the_bob.kml')
        response = login_session.open(route_request)

        cls.login_session = login_session
        cls.kml_data = kml_data

    def test_upload_kml_file(self):
        '''Upload a route from a KML file'''
        def test_retrieve():
            retrieve_response = self.login_session.open(self.url)
            document = retrieve_response.read().strip()
            self.assertTrue(document.startswith('<?xml'), "Not an xml document")
            self.assertTrue(document.endswith('</kml>'), 'Not a KML document')
            self.assertGreater(document.count('<coordinates>'), 0, 'Has no coordinates')
            self.assertGreater(document.count('The Bob'), 0, 'Is not the plan_c kml document')

        utils.try_until(2, test_retrieve)

    def test_change_route(self):
        '''Upload a new route overwritting an existing one'''
        route_request, kml_data = self.create_upload_request('the_bob2.kml')
        response = self.login_session.open(route_request)

        def test_retrieve():
            retrieve_response = self.login_session.open(self.url)
            document = retrieve_response.read().strip()
            self.assertTrue(document.startswith('<?xml'), "Not an xml document")
            self.assertTrue(document.endswith('</kml>'), 'Not a KML document')
            self.assertGreater(document.count('<coordinates>'), 1, 'Has no coordinates')
            self.assertGreater(document.count('plan_c'), 0, 'Is not the plan_c kml document')
        utils.try_until(2, test_retrieve)

class TestGPXRouteUpload(unittest.TestCase):

    def create_upload_request(self, filename):
        headers = {
                'Content-Type': 'multipart/form-data; boundary=formboundary'
                }

        dir_path = os.path.dirname(__file__)
        kml_path = os.path.join(dir_path, filename)
        kml_data = open(kml_path, 'r').read()
        
        post_body_lines = [
                '--formboundary',
                'Content-Disposition: form-data; name="userfile"; filename=%s' % filename,
                'Content-Type: text/xml',
                '',
                kml_data,
                '',
                '--formboundary--'
                ]
        post_body = '\r\n'.join(post_body_lines)
        headers['Content-Length'] = len(post_body)

        route_request = urllib2.Request(
                self.url,
                data=post_body,
                headers=headers
               ) 
        return route_request, kml_data

    def setUp(cls):
        env = environment.create()
        env.make_pristine()
        env.bringup_infrastructure()

        douglas = env.douglas
        env.create_user(douglas)
        login_session = douglas.login()

        trips = env.trips.add_trips_to_user(douglas, env.data['trips'])
        trip = trips[0]

        url = env.trailhead_url + '/trips/%s/map/route' % trip['id']
        cls.url = url


        route_request, kml_data = cls.create_upload_request('the_bob.gpx')
        response = login_session.open(route_request)

        cls.login_session = login_session
        cls.kml_data = kml_data

    def test_upload_kml_file(self):
        '''Upload a route from a KML file'''
        dir_path = os.path.dirname(__file__)
        kml_path = os.path.join(dir_path, 'the_bob_gpx_converted.kml')
        expected_kml_data = open(kml_path, 'r').read()

        def test_retrieve():
            retrieve_response = self.login_session.open(self.url)
            document = retrieve_response.read().strip()
            passed = document.startswith('<?xml') and \
                    document.endswith('</kml>') and \
                    document.count('<coordinates>') > 1
            self.assertTrue(passed)

        utils.try_until(2, test_retrieve)


if __name__ == '__main__':
    unittest.main()

