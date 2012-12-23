import json
import logging
import os

from datetime import datetime

from tornado import web, template

from trailhead.handlers import BaseHandler

def passwordreset_factory(environ):
    return PasswordReset

class PasswordReset(BaseHandler):

    def __init__(self, *args, **kwargs):
        BaseHandler.__init__(self, *args, **kwargs)
        self.service = self.application.mq.remoting.service('Adventurer')
        self.remoting = self.application.mq.remoting

    @web.asynchronous
    def post(self):
        body = json.loads(self.request.body)

        command = self.service.reset_password(body['email'])
        command.persistant = True
        self.remoting.call(command, callback=self.handle_result)

    @web.asynchronous
    def get(self, reset_key):
        template_path = os.path.join(os.path.join(os.path.realpath(__file__) + '/../'), 'templates')
        title = 'Create new password'
        login_message = 'Enter you email address and a new password.'

        loader = template.Loader(template_path)
        html_content = loader.load('reset.html').generate(
            message = login_message,
            title = title,
            key = reset_key
            )

        class HandleResult(object):

            def handle_result(callback, body):
                if body:
                    self.write(html_content)
                else:
                    self.write('bye')
                self.finish()

            def handle_error(callback, code, message, data):
                self.respond_with_error(code, message, data)

        command = self.service.validate_reset_key(reset_key)
        command.persistant = True
        self.remoting.call(command, callback=HandleResult())

    @web.asynchronous
    def put(self, reset_key):
        body = json.loads(self.request.body)
        class HandleResult(object):

            def handle_result(callback, result):
                if result:
                    self.set_secure_cookie("user", body['email'])
                self.finish()

            def handle_error(callback, code, message, data):
                self.respond_with_error(code, message, data)

        command = self.service.reset_change_password(reset_key, body['email'], body['password'])
        command.persistant = True
        self.remoting.call(command, callback=HandleResult())


    def respond_to_request(self, body):
        self.set_header('Content-Type', 'application/json')
        self.set_status(200)
        self.write(json.dumps({'reset': True}))
        self.finish()

        

