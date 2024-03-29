import logging

import json
import uuid
import pika

from trailhead.handlers import BaseHandler

from tornado import web

def userhandler_factory(environ):
    return UserHandler

class UserHandler(BaseHandler):

    @web.asynchronous
    def get(self):
        if not self.current_user:
            raise web.HTTPError(403)

        logging.info('TrailHead(UserHandler): GET /user (%s)' % self.current_user)
        remoting = self.application.mq.remoting
        service = remoting.service('Adventurer')
        command = service.get(self.current_user)
        remoting.call(command, callback=self.respond_to_get)
        logging.debug('TrailHead(UserHandler): Publish request to adventurer.rpc (id: %s)' % command.message_id)

    def respond_to_get(self, body):
        logging.debug('TrailHead(UserHandler): Received response %s' % body)
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(body)
        self.finish()

