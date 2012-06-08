import logging
import json
from tornado import web

class BaseHandler(web.RequestHandler):
    def __init__(self, *args, **kwargs):
        web.RequestHandler.__init__(self, *args, **kwargs)

        class HandleResult(object):

            def handle_result(callback, body):
                self.respond_to_request(body)

            def handle_error(callback, code, message, data):
                self.respond_with_error(code, message, data)

        self.handle_result = HandleResult()

    def get_current_user(self):
        return self.get_secure_cookie("user")

    def respond_with_error(self, code, message, data):
        logging.debug('Received error: %s' % message)
        self.set_status(500)
        self.set_header('X-Error-Message', message)
        self.write(json.dumps(message))
        self.finish()
        

