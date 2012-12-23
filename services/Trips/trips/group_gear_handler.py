
import json
import logging

from tornado import web

from trailhead.handlers import BaseHandler

def create_groupgearhandler(environ):
    return GroupGearHandler

class GroupGearHandler(BaseHandler):

    def __init__(self, *args, **kwargs):
        BaseHandler.__init__(self, *args, **kwargs)
        self.service = self.application.mq.remoting.service('Trips')
        self.remoting = self.application.mq.remoting

    @web.authenticated
    @web.asynchronous
    def get(self, trip_id):
        command = self.service.get_group_gear(trip_id)
        self.remoting.call(command, self.handle_result)

    @web.authenticated
    def put(self, trip_id, gear_id):
        self.set_header('Content-Type', 'application/json')
        gear = json.loads(self.request.body)
        command = self.service.share_gear(trip_id, gear)
        command.persistant = True
        self.remoting.call(command)
        self.write(self.request.body)

    @web.authenticated
    @web.asynchronous
    def post(self, trip_id):
        self.set_header('Content-Type', 'application/json')
        gear = json.loads(self.request.body)
        command = self.service.share_gear(trip_id, gear)
        command.persistant = True
        self.remoting.call(command, self.handle_result)

    @web.authenticated
    def delete(self, trip_id, gear_id):
        command = self.service.unshare_gear(trip_id, gear_id)
        command.persistant = True
        self.remoting.call(command)

    def respond_to_request(self, body):
        logging.debug('Received response:\n%s' % body)
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(body))
        self.finish()
