
class Application(object):
    
    def __init__(self, daemonizer=None, pidfile=None, pika_params=None, 
            pika_connection=None):
        self.daemonizer = daemonizer
        self.pidfile = pidfile
        self.pika_params = pika_params
        self.pika_connection = pika_connection

    def run(self):
        self.daemoncontext = self.daemonizer(pidfile=self.pidfile)
        with self.daemoncontext:
            connection = self.pika_connection(self.pika_params,
                    self.on_connection_opened)
            connection.ioloop.start()

    def on_connection_opened(self, connection):
        self.connection = connection
        self.open_channel()

    def open_channel(self):
        self.connection.channel(self.on_channel_opened)

    def on_channel_opened(self, channel):
        self.channel = channel
        self.begin_consuming()

    def begin_consuming(self):
        self.channel.basic_consume(self.process_registration, queue='registrations')

    def process_registration(self):
        pass

        
