from tornado import web
import pika

import uuid
import json

import logging

from trailhead.handlers import BaseHandler

class UserGearListHandler(BaseHandler):

    def __init__(self, *args, **kwargs):
        BaseHandler.__init__(self, *args, **kwargs)
        self.service = self.application.mq.remoting.service('Gear')
        self.remoting = self.application.mq.remoting

    @web.authenticated
    @web.asynchronous
    def get(self):
        adventurer = self.get_current_user()
        logging.info('Received request for %s\'s gear list' % adventurer)
        command = self.service.list(adventurer)
        self.remoting.call(command, callback=self.handle_result)

    @web.authenticated
    @web.asynchronous
    def post(self):
        adventurer = self.get_current_user()
        pieceofgear = json.loads(self.request.body)
        command = self.service.create(adventurer, pieceofgear)
        self.remoting.call(command, callback=self.handle_result)

    @web.authenticated
    @web.asynchronous
    def put(self, gear_id):
        adventurer = self.get_current_user()
        pieceofgear = json.loads(self.request.body)
        logging.info("Received gear update for %s:%s" % (adventurer, gear_id))
        command = self.service.update(adventurer, gear_id, pieceofgear)
        self.remoting.call(command, callback=self.handle_result)

    @web.authenticated
    def delete(self, owner, gear_id):
        logging.info("Received gear delete for %s:%s" % (owner, gear_id))
        command = self.service.delete(owner, gear_id)
        self.remoting.call(command)
        self.set_status(204)

    def respond_to_request(self, body):
        logging.debug('Received response:\n%s' % body)
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(body))
        self.finish()



