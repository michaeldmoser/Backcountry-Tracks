import json
import logging

from tornado import web

from trailhead.handlers import BaseHandler

class FriendsHandler(BaseHandler):
    '''
    Manages friends on a trip
    '''

    def __init__(self, *args, **kwargs):
        BaseHandler.__init__(self, *args, **kwargs)
        self.service = self.application.mq.remoting.service('Trips')
        self.remoting = self.application.mq.remoting

    @web.authenticated
    @web.asynchronous
    def post(self, trip_id):
        invite = json.loads(self.request.body)
        command = self.service.invite(trip_id, self.current_user, invite)
        command.persistant = True
        self.remoting.call(command, self.respond_to_request)

    def respond_to_request(self, body):
        logging.debug('Received response:\n%s' % body)
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(body))
        self.finish()

