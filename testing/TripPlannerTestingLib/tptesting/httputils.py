import unittest
import urllib2
import json

from tptesting import environment

class JsonRequest(urllib2.Request):

    def __init__(self, url, data=None, headers={},
                 origin_req_host=None, unverifiable=False, method='POST'):
        env = environment.create()
        self.method = method

        headers['Content-Type'] = 'appliction/json'
        json_data = json.dumps(data)

        full_url = env.trailhead_url + url

        urllib2.Request.__init__(self, full_url, data=json_data, headers=headers,
                origin_req_host=origin_req_host, unverifiable=unverifiable)

    def get_method(self):
        return self.method

class SystemTestFixture(unittest.TestCase):
    '''
    The SystemTestFixture sets up the basic BCT environment with a user,
    trips and gear to make testin simplier. The user used is Douglas.

    This class defines the "setUpClass" classmethod() and calls postSetUpClass()
    as a classmethod(). You can do additional work in postSetUpClass() that you 
    would normal wish to do in setUpClass().

    The user is already logged in. You access the urllib2 session with the
    login_session attribute. 

    Also available as a classmethod() is perform_request. This method will perform
    a JSON request and will set the response attribute and will return a dict()
    create from the resulting json return from the request.
    '''

    @classmethod
    def setUpClass(cls):
        env = environment.create()
        env.make_pristine()
        env.bringup_infrastructure()

        douglas = env.douglas
        env.create_user(douglas)
        cls.login_session = douglas.login()
        cls.env = env
        cls.user = douglas

        cls.trips = env.trips.add_trips_to_user(douglas, env.data['trips'])
        cls.gear = env.gear.add_gear_to_user(douglas, env.data['gear'])

        cls.postSetUpClass()

    @classmethod
    def perform_request(self, url, post_data=None, method='POST'):
        comment_post_request = JsonRequest(url, data=post_data, method=method)
        response = self.login_session.open(comment_post_request)
        self.response = response

        return json.loads(self.response.read())


        


