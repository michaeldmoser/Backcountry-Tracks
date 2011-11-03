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

#class TestAdventurerServiceRegistration(unittest.TestCase):
class TestAdventurerServiceRegistration():
    @classmethod
    def setUpClass(cls):
        cls.environ = environment.create()
        cls.environ.make_pristine()

        cls.environ.rabbitmq.start_server()
        cls.environ.riak.start()

        mq_params = pika.ConnectionParameters(host='localhost')
        mq_conn = pika.BlockingConnection(mq_params)
        channel = mq_conn.channel()
        channel.exchange_declare(exchange='registration', type='topic')
        channel.queue_declare(
                queue = 'register',
                durable = False,
                exclusive = False,
                auto_delete = True
                )
        channel.queue_bind(
                exchange = 'registration',
                queue = 'register',
                routing_key = 'registration.register'
                )
        cls.channel = channel

        cls.environ.adventurer.start()

        cls.albert = cls.environ.albert

        adventurer_config = cls.environ.get_config_for('adventurer')
        cls.pidfile_path = adventurer_config['pidfile']

    @classmethod
    def tearDownClass(cls):
        cls.environ.teardown()

    def notest_daemonized_process(self):
        '''We should have a running process with a pidfile'''
        def check_for_pidfile():
            assert path.exists(self.pidfile_path), 'PID file does not exist'
        utils.try_until(1, check_for_pidfile)

        pid = open(self.pidfile_path, 'r').read().strip()
        cmdline_path = path.join('/proc', pid, 'cmdline')
        assert path.exists(cmdline_path), 'Could not find the process'

        cmdline = open(cmdline_path, 'r').read()
        assert '/usr/local/bin/adventurer' in cmdline, 'Not the correct process'

    def notest_retrieves_and_saves_regitrations(self):
        """Service should retrieve registrations from rabbitmq and save to riak"""
        registration_message = json.dumps(self.environ.albert)
        properties = pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2
                )

        self.channel.basic_publish(
                exchange='registration',
                routing_key='registration.register',
                properties=properties,
                body=registration_message
                )

        def check_registration_stored():
            try:
                user_bucket = self.environ.riak.get_database('adventurers')
                albert_user = user_bucket.get(self.albert.email)
                albert_data = albert_user.get_data()
            except Exception, e:
                raise AssertionError(str(e))

            # remove confirmation key from data so we
            # get a true comparison
            del albert_data['confirmation_key']
            self.assertEquals(albert_data, self.albert)
        utils.try_until(1, check_registration_stored)

    def notest_regitration_sends_confirmation_email(self):
        """Service should sends confirmation email for upon registration"""
        registration_message = json.dumps(self.environ.albert)
        properties = pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2
                )

        self.channel.basic_publish(
                exchange='registration',
                routing_key='registration.register',
                properties=properties,
                body=registration_message
                )

        self.environ.clear_mbox()
        mbox_path = self.environ.get_config_for('mbox_file')
        self.mbox = mailbox.mbox(mbox_path)
        assert len(self.mbox) == 0, 'Mailbox not pristine'

        def check_email_sent():
            mbox_path = self.environ.get_config_for('mbox_file')
            mbox = mailbox.mbox(mbox_path)
            assert len(mbox) == 1

        utils.try_until(1, check_email_sent)

    def notest_email_contains_link_for_completing_registration(self):
        """Confirmation email contains link to complete registration"""
        registration_message = json.dumps(self.environ.albert)
        properties = pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2
                )

        self.channel.basic_publish(
                exchange='registration',
                routing_key='registration.register',
                properties=properties,
                body=registration_message
                )

        self.environ.clear_mbox()
        mbox_path = self.environ.get_config_for('mbox_file')
        self.mbox = mailbox.mbox(mbox_path)
        assert len(self.mbox) == 0, 'Mailbox not pristine'

        def get_email_message():
            mbox_path = self.environ.get_config_for('mbox_file')
            mbox = mailbox.mbox(mbox_path)
            assert len(mbox) == 1

        utils.try_until(1, get_email_message)

        self.mbox = mailbox.mbox(mbox_path)
        for key, message in self.mbox.items():
            continue

        trailhead_url = self.environ.get_config_for('trailhead_url')
        url = 'href="%s/activate/%s/' % (trailhead_url, self.albert['email'])
        self.assertIn(url, message.as_string())

    def notest_confirmation_request_activates_account(self):
        pass
#        urllib2.urlopen(self.register_url)
#
#        def check_registration_complete():
#            try:
#                user_bucket = self.environ.riak.get_database('adventurers')
#                albert_user = user_bucket.get(self.albert.email)
#                albert_data = albert_user.get_data()
#            except Exception, e:
#                raise AssertionError(str(e))
#
#            self.assertTrue(albert_data['registration_complete'])
#
#        utils.try_until(1, check_registration_complete)

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

if __name__ == '__main__':
    unittest.main()

