
class PikaClient(object):
    def __init__(self, connection, params):
        self.connection = connection
        self.params = params

    def connect(self):
        self.connection(self.params)
