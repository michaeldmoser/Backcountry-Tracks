
class SmokeSignalApp(object):
    def __init__(self, pika_connection=None):
        self.pika_connection = pika_connection

    def run(self):
        channel = self.pika_connection.channel()

        # register
        channel.exchange_declare(exchange = 'registration', durable = True,
                type = 'topic')
        channel.queue_declare(queue = 'register_rpc', durable=True)
        channel.queue_bind(queue = 'register_rpc', exchange = 'registration',
                routing_key = 'registration.register')

        # activate
        channel.queue_declare(queue = 'activate_rpc', durable=True)
        channel.queue_bind(queue = 'activate_rpc', exchange = 'registration',
                routing_key = 'registration.activate')

        # login
        channel.exchange_declare(exchange = 'adventurer', durable = True,
                type = 'topic')
        channel.queue_declare(queue = 'login_rpc', durable=True)
        channel.queue_bind(queue = 'login_rpc', exchange = 'adventurer',
                routing_key = 'adventurer.login')
