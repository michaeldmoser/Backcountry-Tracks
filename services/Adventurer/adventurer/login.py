import pika
import uuid
import json
import os
from tornado import web, template

import logging

from trailhead.handlers import BaseHandler


class LoginHandler(BaseHandler):
    def get(self):
        template_path = os.path.join(os.path.join(os.path.realpath(__file__) + '/../'), 'templates')
        loader = template.Loader(template_path)

        title = 'Login'
        login_message = 'Please login:'

        reason = self.get_cookie('force_login_reason')
        if reason == 'invalid_login':
            login_message = 'Your username or password is incorrect. Please try again:'
        elif reason == 'registration_complete':
            title = 'Registration Complete'
            login_message = 'Your registration is complete! Login to continue:'

        self.clear_cookie('force_login_reason')

        html = loader.load('login.html').generate(
            message = login_message,
            title = title
            )
        self.write(html)
        self.finish()

    @web.asynchronous
    def post(self):
        if 'application/json' not in self.request.headers.get('Content-Type'):
            self.set_status(400)
            self.finish()
            return

        remoting = self.application.mq.remoting
        service = remoting.service('Adventurer')

        credentials = json.loads(self.request.body)
        command = service.login(**credentials)

        remoting.call(command, callback=self.respond_to_login)

    def respond_to_login(self, body):
        logging.debug('Got response for %s' % body)
        if body['successful'] == True:
            self.set_secure_cookie("user", body['key'])
            self.write({'location': '/app/home'})
            self.set_status(202)
        else:
            self.set_cookie("force_login_reason", 'invalid_login')
            self.write({'location': '/app/login'})
            self.set_status(403)

        self.finish()

class LogoutHandler(BaseHandler):
    def post(self):
        self.clear_all_cookies();
        self.write({"logout": True})
        self.set_status(204)

