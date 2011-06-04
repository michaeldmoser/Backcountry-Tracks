class PikaChannelFake(object):
    def basic_publish(self, exchange=None, routing_key=None, body=None, properties=None):
        self.message_body = body

class PikaConnectionFake(object):
    def __init__(self, params, on_open_callback=None):
        if on_open_callback is not None:
            on_open_callback(self)

    def channel(self, callback=None):
        if callback is not None:
            callback(PikaChannelFake())


