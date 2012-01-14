import json
import logging

from tornado import web

from trailhead.handlers import BaseHandler

class GearHandler(BaseHandler):

    def __init__(self, *args, **kwargs):
        BaseHandler.__init__(self, *args, **kwargs)
        self.service = self.application.mq.remoting.service('Trips')
        self.remoting = self.application.mq.remoting

    @web.authenticated
    @web.asynchronous
    def get(self, trip_id):
        command = self.service.get_personal_gear(trip_id, self.current_user)
        self.remoting.call(command, self.handle_result)

    @web.authenticated
    def put(self, trip_id, gear_id):
        gear = json.loads(self.request.body)
        command = self.service.add_personal_gear(trip_id, self.current_user, gear)
        command.persistant = True
        self.remoting.call(command)
        self.write(self.request.body)

    @web.authenticated
    def delete(self, trip_id, gear_id):
        command = self.service.remove_personal_gear(trip_id, self.current_user, gear_id)
        command.persistant = True
        self.remoting.call(command)

    def respond_to_request(self, body):
        logging.debug('Received response:\n%s' % body)
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(body))
        self.finish()
