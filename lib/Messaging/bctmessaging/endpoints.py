import pika
import json
import traceback

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

    def process_request(self, channel, mq_method, header, data):
        request = json.loads(data)

        properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = header.correlation_id
                )

        logging.info('Received %s request with correlation id %s' % (request['method'], header.correlation_id))
        method = getattr(self.service, request['method'])
        params = request['params']

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
            logging.error('Exception raised in method %s while processing:\n %s', request['method'], request)
            logging.error(trace_back)
        else:
            if response is None:
                logging.debug('Completed request, no response... %s' % header.correlation_id)
                return
            reply = {
                    'jsonrpc': '2.0',
                    'result': response,
                    'id': properties.correlation_id
                    }
            logging.debug('Response to %s is: %s' % (header.correlation_id, response))
        finally:
            self.channel.basic_ack(delivery_tag=mq_method.delivery_tag)


        self.channel.basic_publish(
                exchange = self.config['reply_exchange'],
                routing_key = 'rpc.reply.%s' % header.reply_to,
                properties = properties,
                body = json.dumps(reply)
                )
