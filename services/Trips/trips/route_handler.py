import json
import logging

from tornado import web

from trailhead.handlers import BaseHandler

class RouteHandler(BaseHandler):

    def __init__(self, *args, **kwargs):
        BaseHandler.__init__(self, *args, **kwargs)
        self.service = self.application.mq.remoting.service('Trips')
        self.remoting = self.application.mq.remoting

    @web.authenticated
    def post(self, trip_id):
        self.set_header('Content-Type', 'application/json')
        file_data = self.request.files['userfile'][0]['body']
        command = self.service.store_route(trip_id, file_data)
        command.persistant = True
        self.remoting.call(command)

        self.write(json.dumps(True))

    @web.authenticated
    @web.asynchronous
    def get(self, trip_id):
        command = self.service.get_route(trip_id)
        command.persistant = True
        self.remoting.call(command, callback=self.handle_result)

    def respond_to_request(self, body): 
        self.set_header('Content-Type', 'application/vnd.google-earth.kml+xml')
        self.set_status(200)
        self.write(body)
        self.finish()

