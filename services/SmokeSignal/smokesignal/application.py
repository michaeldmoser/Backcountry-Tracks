
class SmokeSignalApp(object):
    def __init__(self, pika_connection=None, config={}):
        self.pika_connection = pika_connection
        self.config = config

    def run(self):
        channel = self.pika_connection.channel()

        exchanges = self.config['exchanges']
        for exchange in exchanges:
            channel.exchange_declare(**exchange)

        queues = self.config['queues']
        for queue in queues:
            channel.queue_declare(**queue)

        bindings = self.config['bindings']
        for binding in bindings:
            channel.queue_bind(**binding)


