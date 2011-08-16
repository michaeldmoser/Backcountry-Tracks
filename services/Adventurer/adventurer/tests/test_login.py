import unittest
import types
import json
import uuid
import pika
from pika import spec, frame

from tptesting import environment, fakeriak, fakepika, fakedaemonizer

from adventurer.application import Application
from adventurer.service import Controller

class TestApplicationLogin(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()
        riak_class = fakeriak.RiakClientFake()
        riak_class()
        bucket = riak_class.bucket('adventurer')
        bucket.add_document(self.environ.albert.email, dict(self.environ.albert))

        self.app = Application(bucket = bucket)

    def test_login_successful(self):
        '''Returns successful message on valid credentials'''
        login_result = self.app.login(self.environ.albert.email,
                self.environ.albert.password)
        self.assertTrue(login_result)

    def test_login_invalid(self):
        '''Returns false on bad password'''
        login_result = self.app.login(self.environ.albert.email, 'badpassword')
        self.assertFalse(login_result)

    def test_login_casts_unicode_email_to_string(self):
        """Login allows Unicode email"""
        class RiakBucketSpy(object):
            def get(spy, key):
                spy.key = key
                class RiakObjectSpy(object):
                    def get_data(rspy):
                        return dict(password='mypass')
                return RiakObjectSpy()
        riakspy = RiakBucketSpy()

        app = Application(bucket = riakspy)
        app.login(unicode('email@test.com'), 'mypass')

        self.assertEquals(type(riakspy.key), types.StringType)

class TestServiceLogin(unittest.TestCase):

    def test_receives_login_message(self):
        '''Controller should consume from login_rpc and publish result'''
        environ = environment.create()

        daemonizer = fakedaemonizer.Daemonizer()
        pidfile = fakedaemonizer.PidFile()
        riak_class = fakeriak.RiakClientFake()
        riak_class()
        bucket = riak_class.bucket('adventurer')
        bucket.add_document(environ.douglas.email, dict(environ.douglas))

        app = Application(bucket = bucket)
        def application_injector():
            return app

        pika_class = fakepika.SelectConnectionFake()
        login_message = json.dumps({
            'email': environ.douglas.email,
            'password': environ.douglas.password
            })
        method = frame.Method(1, spec.Basic.ConsumeOk())
        properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = str(uuid.uuid4()),
                reply_to = str(uuid.uuid4())
                )

        pika_class.inject('login_rpc', properties, login_message)

        controller = Controller(
                daemonizer = daemonizer,
                pidfile = pidfile,
                pika_params = dict(),
                pika_connection = pika_class,
                application = application_injector
                )
        controller.run()

        pika_class.trigger_consume('login_rpc')

        message = pika_class.published_messages[0]
        expected_message = {
                'exchange': 'adventurer',
                'routing_key': 'adventurer.login.%s' % properties.reply_to,
                'correlation_id': properties.correlation_id,
                'content_type': properties.content_type,
                'body': {'successful': True, 'email': environ.douglas.email}
                }

        actual_message = {
                'exchange': message.exchange,
                'routing_key': message.routing_key,
                'correlation_id': message.properties.correlation_id,
                'content_type': message.properties.content_type,
                'body': json.loads(message.body),
                }

        self.assertEquals(actual_message, expected_message)



if __name__ == '__main__':
    unittest.main()
