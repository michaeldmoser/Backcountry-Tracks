import pika
import json
import traceback

import logging

class MessagingEndpointServiceController(object):
    '''
    Decomposes JSON-RPC messages from the AMQP server and converts them
    to method calls on the a service

    Follows a "Front Controller" like pattern (See Patterns of Enterprise Application
    Architecture p344) but in the context of a messaging system instead of web
    requests.
    '''

    def __init__(self, recv_channel, pub_channel, configuration, services,
            remoting_client):
        self.recv_channel = recv_channel
        self.pub_channel = pub_channel
        self.config = configuration
        self.services = services

    def start(self):
        rpc_queue = self.config['queues']['rpc']

        logging.debug("My Configuration: %s" % self.config)
        self.recv_channel.basic_consume(self.process_request, queue=rpc_queue)


    def send_reply(self, reply, correlation_id, reply_to):
        properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = correlation_id
                )

        self.pub_channel.basic_publish(
                exchange = self.config['reply_exchange'],
                routing_key = 'rpc.reply.%s' % reply_to,
                properties = properties,
                body = json.dumps(reply)
                )

    def process_request(self, channel, mq_method, header, data):
        channel.basic_ack(delivery_tag=mq_method.delivery_tag)

        request = json.loads(data)
        routing_key = mq_method.routing_key


        try:
            service = self.services.get(routing_key)
            
            method = getattr(service, request['method'])
            params = request['params']
        except (AttributeError, TypeError) as err:
            reply = {
                'jsonrpc': '2.0',
                'id': header.correlation_id,
                'error': {
                    'code': -32601,
                    'message': str(err)
                    }
                }

            self.send_reply(reply, header.correlation_id, header.reply_to)

        logging.info('Received %s request with correlation id %s' %
                (request['method'], header.correlation_id))
        try:
            if isinstance(params, dict):
                response = method(**request['params'])
            elif isinstance(params, list):
                response = method(*request['params'])
        except Exception as err:
            reply = {
                'jsonrpc': '2.0',
                'id': header.correlation_id,
                'error': {
                    'code': -32000,
                    'message': str(err)
                    }
                }
            trace_back = traceback.format_exc()
            logging.error('Exception raised in method %s while processing %s',
                    request['method'], header.correlation_id)
            logging.error(trace_back)

            self.send_reply(reply, header.correlation_id, header.reply_to)
        else:
            if not header.correlation_id:
                return

            reply = {
                    'jsonrpc': '2.0',
                    'result': response,
                    'id': header.correlation_id
                    }
            self.send_reply(reply, header.correlation_id, header.reply_to)

class EntryPoint(object):

    def assemble_service(self):
        bucket_name = self.config['database']['bucket']
        riak = RiakClient(self.config['database']['host'])

        remoting_client = RemotingClient(self.service_channel)

        return TripsDb(remoting_client, riak, bucket_name, self.config['url'],
                converter=GPSFormatConverter)

    def __init__(self, configuration, environ):
        self.environ = environ
        self.config = configuration

    def start(self):
        self.environ.open_messaging_channel(self.on_service_channel_opened)

    def on_service_channel_opened(self, channel):
        self.service_channel = channel
        connection = channel.transport.connection
        connection.channel(self.on_controller_channel_opened)

    def on_controller_channel_opened(self, channel):
        self.channel = channel

        service = ServiceBuilder(self.config['services'])
        controller = MessagingEndpointServiceController(self.channel,
                self.service_channel, self.config, services)
        controller.start()

