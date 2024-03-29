
class MessagingBuilder(object):
    def __init__(self, config):
        self.connection = None
        self.config = config

    def __pika_connection(self):
        from pika import SelectConnection, ConnectionParameters
        return SelectConnection, ConnectionParameters

    def __call__(self, on_channel_callback):
        self.on_channel_callback = on_channel_callback

        Connection, Parameters = self.__pika_connection()
        params = Parameters(**self.config['messaging']['connection_params'])
        conn = Connection(params, on_open_callback=self.on_connection_opened)
        conn.ioloop.start()

    def on_connection_opened(self, connection):
        self.connection = connection
        self.connection.channel(self.on_channel_opened)

    def on_channel_opened(self, channel):
        self.channel = channel
        self.on_channel_callback(self.channel)

# FIXME: I don't like the location of this function.
def messaging_builder_factory(environ):
    return MessagingBuilder(environ.config)

