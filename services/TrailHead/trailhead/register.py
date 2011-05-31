from tornado.web import RequestHandler

class RegisterHandler(RequestHandler):
    def post(self):
        self.set_status(202)

