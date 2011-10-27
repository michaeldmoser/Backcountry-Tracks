
class Environment(object):
    def __init__(self, config, messaging_builder):
        self.config = config
        self.messaging_builder = messaging_builder

    def open_messaging_channel(self, on_channel_callback):
        self.messaging_builder(on_channel_callback)

