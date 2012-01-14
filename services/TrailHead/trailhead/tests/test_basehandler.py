import unittest

import json
import pika
import uuid

from tptesting import faketornado, environment, fakepika, thandlers

from trailhead.tests.utils import create_fake_application, setup_handler
from trailhead.handlers import BaseHandler

class TestHandleErrors(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()

        class HandlerSpy(BaseHandler):
            def __init__(self, *args, **kwargs):
                BaseHandler.__init__(self, *args, **kwargs)
                self.service = self.application.mq.remoting.service('Trips')
                self.remoting = self.application.mq.remoting

            def get(self):
                command = self.service.list()
                self.remoting.call(command, self.handle_result)

        url = '/app/trips'
        self.handler, self.application, self.pika = setup_handler(HandlerSpy,
                'GET', url, user=self.environ.douglas.email)
        self.request = self.handler.request

        self.handler.get()
        sent_message = self.pika.published_messages[0]

        self.headers = pika.BasicProperties(
                correlation_id = sent_message.properties.correlation_id,
                content_type = 'application/json'
                )

        self.rpc_response = {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32000,
                    'message': 'Generic error message',
                    },
                'id': sent_message.properties.correlation_id
                }

        reply_queue = self.application.mq.remoting.queue

        self.pika.inject(reply_queue, self.headers, json.dumps(self.rpc_response))
        self.pika.trigger_consume(reply_queue)

    def test_response_status(self):
        '''JSON-RPC errors should produce an HTTP 500 status code'''
        self.assertEquals(self.handler._status_code, 500)

    def test_respone_message(self):
        '''JSON-RPC errors whould produce generic http status message'''
        self.assertEquals('Generic error message', self.handler._headers['X-Error-Message'])

if __name__ == '__main__':
    unittest.main()

