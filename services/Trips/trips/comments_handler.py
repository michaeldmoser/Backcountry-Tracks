import json
import logging

from datetime import datetime

from tornado import web

from trailhead.handlers import BaseHandler

class CommentsHandler(BaseHandler):

    def __init__(self, *args, **kwargs):
        BaseHandler.__init__(self, *args, **kwargs)
        self.service = self.application.mq.remoting.service('Trips.Comments')
        self.remoting = self.application.mq.remoting

    @web.authenticated
    @web.asynchronous
    def post(self, trip_id):
        body = json.loads(self.request.body)
        command = self.service.add(trip_id, body)
        command.persistant = True
        self.remoting.call(command, self.handle_result)

    @web.authenticated
    @web.asynchronous
    def get(self, trip_id):
        command = self.service.list(trip_id)
        self.remoting.call(command, self.handle_result)

    def respond_to_request(self, body): 
        self.set_header('Content-Type', 'application/json')
        self.set_status(200)
        self.write(json.dumps(body))
        self.finish()


