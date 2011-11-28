import json
import pika
import uuid
from tornado import web
from tornado.web import RequestHandler
from trailhead.handlers import BaseHandler

class RegisterHandler(BaseHandler):

    def get(self):
        self.set_status(400)
        return

    @web.asynchronous
    def post(self):
        if 'application/json' not in self.request.headers.get('Content-Type'):
            self.set_status(400)
            self.finish()
            return

        remoting = self.application.mq.remoting
        service = remoting.service('Adventurer')
        registration_data = json.loads(self.request.body)
        command = service.register(**registration_data)
        command.persistant = True

        remoting.call(command, callback=self.respond_to_request)

    def respond_to_request(self, headers, body):
        reply = json.loads(body)
        self.write(reply)
        self.finish()

class ActivateHandler(BaseHandler):
    @web.asynchronous
    def get(self, email, confirmation_code):
        remoting = self.application.mq.remoting
        service = remoting.service('Adventurer')
        registration_data = json.loads(self.request.body)
        command = service.activate(email, confirmation_code)
        command.persistant = True

        remoting.call(command, callback=self.respond_to_request)

    def respond_to_request(self, headers, body):
        reply = json.loads(body)
        if reply['successful'] == True:
            self.set_status(303)
            self.set_cookie("force_login_reason", 'registration_complete')
            self.set_header('Location', '/app/login')
        else:
            self.set_status(403)
            self.set_header('Location', '/')
        self.finish()

