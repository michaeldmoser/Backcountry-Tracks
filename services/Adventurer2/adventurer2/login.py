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

        mq = self.application.mq
        correlation_id = str(uuid.uuid4())
        properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = correlation_id,
                reply_to = self.application.mq.rpc_reply,
                )
        mq.register_rpc_reply(correlation_id, self.respond_to_login)
        logging.debug('Sending login message for %s' % self.request.body)
        mq.channel.basic_publish(
                exchange = 'adventurer',
                routing_key = 'adventurer.login',
                body = self.request.body,
                properties = properties
                )

    def respond_to_login(self, headers, body):
        logging.debug('Got response for %s' % body)
        reply = json.loads(body)
        if reply['successful'] == True:
            self.set_secure_cookie("user", reply['email'])
#            self.set_header('X-Location', '/app/home')
            self.write({'location': '/app/home'})
            self.set_status(202)
        else:
            self.set_cookie("force_login_reason", 'invalid_login')
#            self.set_header('X-Location', '/app/login')
            self.write({'location': '/app/login'})
            self.set_status(403)

        self.finish()

