import unittest
import urllib2
import json
import pika
import os.path

from urllib2 import HTTPError


from tptesting import environment, utils

from bctmessaging.remoting import RemoteService

class TestRouteUpload(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_upload_kml_file(self):
        '''Upload a route from a KML file'''
        env = environment.create()
        env.make_pristine()
        env.bringup_infrastructure()

        douglas = env.douglas
        env.create_user(douglas)
        login_session = douglas.login()

        trips = env.trips.add_trips_to_user(douglas, env.data['trips'])
        trip = trips[0]

        url = env.trailhead_url + '/trips/%s/map/route' % trip['id']

        headers = {
                'Content-Type': 'multipart/form-data; boundary=formboundary'
                }

        dir_path = os.path.dirname(__file__)
        kml_path = os.path.join(dir_path, 'the_bob.kml')
        kml_data = open(kml_path, 'r').read()
        
        post_body_lines = [
                '--formboundary',
                'Content-Disposition: form-data; name="userfile"; filename=the_bob.kml',
                'Content-Type: application/vnd.google-earth.kml+xml',
                '',
                kml_data,
                '',
                '--formboundary--'
                ]
        post_body = '\r\n'.join(post_body_lines)
        headers['Content-Length'] = len(post_body)

        route_request = urllib2.Request(
                url,
                data=post_body,
                headers=headers
               ) 
        response = login_session.open(route_request)

        def test_retrieve():
            retrieve_response = login_session.open(url)
            self.assertEquals(retrieve_response.read().strip(), kml_data.strip())

        utils.try_until(5, test_retrieve)

        


if __name__ == '__main__':
    unittest.main()

