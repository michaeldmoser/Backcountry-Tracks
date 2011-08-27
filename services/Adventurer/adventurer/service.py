import json
import pika

class Controller(object):

    def __init__(self, daemonizer=None, pidfile=None, pika_params=None,
            pika_connection=None, application=None):
        self.daemonizer = daemonizer
        self.pidfile = pidfile
        self.pika_params = pika_params
        self.pika_connection = pika_connection
        self.application = application

    def run(self):
        self.daemoncontext = self.daemonizer(pidfile=self.pidfile)
        with self.daemoncontext:
            self.app_instance = self.application()
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
        self.channel.basic_consume(self.process_registration, queue='register_rpc')
        self.channel.basic_consume(self.process_login, queue='login_rpc')
        self.channel.basic_consume(self.process_activation, queue='activate_rpc')

    def process_registration(self, channel, method, header, data):
        result = self.app_instance.register(json.loads(data))

        properties = pika.BasicProperties(
                correlation_id = header.correlation_id,
                content_type = 'application/json'
                )

        register_reply = json.dumps(result)
        self.channel.basic_publish(exchange='registration',
                routing_key='registration.register.%s' % header.reply_to,
                properties=properties,
                body=register_reply)
        self.channel.basic_ack(delivery_tag = method.delivery_tag)

    def process_activation(self, channel, method, header, data):
        params = json.loads(data)
        email = params['email']
        confirmation_code = params['confirmation_code']

        result = self.app_instance.activate(email, confirmation_code)

        properties = pika.BasicProperties(
                correlation_id = header.correlation_id,
                content_type = 'application/json'
                )

        activate_reply = json.dumps({
            'successful': result
            })
        self.channel.basic_publish(exchange='registration',
                routing_key='registration.activate.%s' % header.reply_to,
                properties=properties,
                body=activate_reply)
        self.channel.basic_ack(delivery_tag = method.delivery_tag)

    def process_login(self, channel, method, header, data):
        login = json.loads(data)
        result = self.app_instance.login(login['email'], login['password'])

        properties = pika.BasicProperties(
                correlation_id = header.correlation_id,
                content_type = 'application/json'
                )

        login_reply = json.dumps({
            'successful': result,
            'email': login['email']
            })
        self.channel.basic_publish(exchange='adventurer',
                routing_key='adventurer.login.%s' % header.reply_to,
                properties=properties,
                body=login_reply)
        self.channel.basic_ack(delivery_tag = method.delivery_tag)


