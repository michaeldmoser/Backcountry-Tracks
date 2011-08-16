
class SmokeSignalApp(object):
    def __init__(self, pika_connection=None):
        self.pika_connection = pika_connection

    def run(self):
        channel = self.pika_connection.channel()

        # rpc replies
        channel.exchange_declare(exchange = 'rpc_reply', durable = True,
                type = 'topic')

        # register
        channel.exchange_declare(exchange = 'registration', durable = True,
                type = 'topic')
        channel.queue_declare(queue = 'register', durable=True)
        channel.queue_bind(queue = 'register', exchange = 'registration',
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

        # gear
        channel.exchange_declare(exchange = 'gear', durable = True,
                type = 'topic')
        channel.queue_declare(queue = 'user_gear_rpc', durable=True)
        channel.queue_bind(queue = 'user_gear_rpc', exchange = 'gear',
                routing_key = 'gear.user.rpc')
