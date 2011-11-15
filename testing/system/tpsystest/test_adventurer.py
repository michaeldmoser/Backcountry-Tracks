import unittest
import json
from os import path
import uuid
import mailbox
import urllib2
from urllib2 import HTTPError

import pika.adapters
import pika.connection
import pika

from tptesting import environment
from tptesting import utils

class TestAdventurerLogin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        environ = environment.create()
        environ.make_pristine()
        environ.bringup_infrastructure()

        ramona = environ.ramona
        ramona.mark_registered()
        environ.create_user(ramona)

        login_url = environ.trailhead_url + '/login'
        credentials = {
                'email': ramona.email,
                'password': ramona.password
                }

        login_request = urllib2.Request(
                login_url,
                json.dumps(credentials),
                headers = {'Content-Type': 'application/json'}
                )
        cls.response = urllib2.urlopen(login_request)
        cls.response_text = cls.response.read()

    def test_login_successful_reply(self):
        '''User logins with valid credentials via REST API, return new location in response body'''
        location = json.loads(self.response_text)
        expected_location = {"location": "/app/home"}
        self.assertEquals(expected_location, location)

    def test_login_successful_status(self):
        '''User logins with valid credentials via REST API, HTTP status code 202'''
        self.assertEquals(self.response.code, 202)


class TestAdventurerUserData(unittest.TestCase):

    def test_retrieve_user_data(self):
        '''Can retrieve user related data for currently logged in user'''
        environ = environment.create()
        environ.make_pristine()
        environ.bringup_infrastructure()

        ramona = environ.ramona
        ramona.mark_registered()
        environ.create_user(ramona)
        login_session = ramona.login()

        user_profile_url = environ.trailhead_url + '/user'
        request = urllib2.Request(user_profile_url)

        response = login_session.open(request)
        body = response.read()

        user_data = json.loads(body)

        self.assertEquals(user_data, ramona)

class TestAdventurerRegistration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()
        cls.environ.bringup_infrastructure()

        cls.ramona = cls.environ.ramona.registration_data()


        register_url = cls.environ.trailhead_url + '/register'
        cls.request = urllib2.Request(
                register_url,
                json.dumps(cls.ramona),
                headers = {'Content-Type': 'application/json'}
                )

        cls.response = urllib2.urlopen(cls.request)
        cls.body = cls.response.read()

    def test_registrations_saved(self):
        """Service should retrieve registrations from rabbitmq and save to riak"""
        user_bucket = self.environ.riak.get_database('adventurers')
        ramona_user = user_bucket.get(self.ramona['email'])
        ramona_data = ramona_user.get_data()

        # remove confirmation key from data so we
        # get a true comparison
        del ramona_data['confirmation_key']

        self.assertEquals(ramona_data, self.ramona)

    def test_registration_successful_http_status_code(self):
        """Submitting a valid registration should return successful"""
        self.assertEquals(self.response.code, 200)

    def test_regitration_sends_confirmation_email(self):
        """Service should send confirmation email for registration"""
        def check_email_sent():
            mbox_path = self.environ.get_config_for('mbox_file')
            mbox = mailbox.mbox(mbox_path)
            assert len(mbox) == 1

        utils.try_until(1, check_email_sent)

    def test_email_contains_link_for_completing_registration(self):
        """Confirmation email contains link to complete registration"""
        mbox_path = self.environ.get_config_for('mbox_file')
        def get_email_message():
            mbox = mailbox.mbox(mbox_path)
            assert len(mbox) == 1

        utils.try_until(1, get_email_message)

        self.mbox = mailbox.mbox(mbox_path)
        for key, message in self.mbox.items():
            continue

        trailhead_url = self.environ.get_config_for('trailhead_url')
        url = 'href="%s/activate/%s/' % (trailhead_url, self.ramona['email'])
        self.assertIn(url, message.as_string())


if __name__ == '__main__':
    unittest.main()

