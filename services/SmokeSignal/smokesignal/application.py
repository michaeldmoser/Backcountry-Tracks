
class SmokeSignalApp(object):
    def __init__(self, pika_connection=None):
        self.pika_connection = pika_connection

    def run(self):
        channel = self.pika_connection.channel()

        channel.exchange_declare(exchange = 'registration', durable = True, 
                type = 'topic')
        channel.queue_declare(queue = 'register', durable=True)
        channel.queue_bind(queue = 'register', exchange = 'registration',
                routing_key = 'registration.register')
