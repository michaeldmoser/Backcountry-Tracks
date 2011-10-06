import pika
import json

import logging


class MessagingEndPointController(object):
    '''
    Decomposes JSON-RPC messages from the AMQP server and converts them
    to method calls on the provided @service

    Follows a "Front Controller" like pattern (See Patterns of Enterprise Application
    Architecture p344) but in the context of a messaging system instead of web
    requests.
    '''

    def __init__(self, channel, configuration, service):
        self.channel = channel
        self.config = configuration
        self.service = service

    def start(self):
        rpc_queue = self.config['queues']['rpc']

        logging.debug("My Configuration: %s" % self.config)
        self.channel.basic_consume(self.process_request, queue=rpc_queue)

    def process_request(self, channel, method, header, data):
        request = json.loads(data)

        properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = header.correlation_id
                )

        logging.info('Received %s request' % request['method'])
        method = getattr(self.service, request['method'])
        params = request['params']

        if isinstance(params, dict):
            response = method(**request['params'])
        elif isinstance(params, list):
            response = method(*request['params'])

        if response is None:
            return

        logging.debug('Publish response to %s to routing key %s' % (header.correlation_id, header.reply_to))
        self.channel.basic_publish(
                exchange = self.config['reply_exchange'],
                routing_key = header.reply_to,
                properties = properties,
                body = json.dumps(response)
                )
