import pika
import uuid
import json

from tptesting import fakepika, environment

from bctmessaging.endpoints import MessagingEndPointController

def create_messaging_channel():
    '''
    Creates a SelectConnectionFake pika connection and
    returns a channel and the pika connection
    '''
    mq = fakepika.SelectConnectionFake()
    mq.ioloop.start()
    channel = mq._channel

    return channel, mq

def create_endpoint_sut(service_double, method_name, queue_name="rpc_queue",
       reply_exchange_name="rpc_rpley", rpc_args=[], trigger=True):
    '''
    Builds a MessagingEndPointController for testing and then injects a message
    for consumption. Will trigger consuming the message unless @trigger is False
    '''
    env = environment.create()
    channel, mq = create_messaging_channel()

    config = {'queues': {'rpc': queue_name}, 'reply_exchange': reply_exchange_name}

    controller = MessagingEndPointController(channel, config, service_double)
    controller.start()

    properties = pika.BasicProperties(
            content_type = 'application/json',
            correlation_id = str(uuid.uuid4()),
            reply_to = str(uuid.uuid4())
            )
    request = {
            'jsonrpc': '2.0',
            'method': method_name,
            'params': rpc_args,
            'id': properties.correlation_id,
            }

    mq.inject(queue_name, properties, json.dumps(request))
    if trigger:
        mq.trigger_consume(queue_name)

    return mq, request, properties

