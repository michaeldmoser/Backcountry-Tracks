from pika import frame, spec
import logging

class PikaChannelFake(object):
    def basic_publish(self, exchange=None, routing_key=None, body=None, properties=None):
        self.message_body = body

class PikaConnectionFake(object):
    def __init__(self, params, on_open_callback=None):
        if on_open_callback is not None:
            on_open_callback(self)

    def channel(self, callback=None):
        if callback is not None:
            callback(PikaChannelFake())

class PikaMessage(object):
    def __init__(self, exchange, routing_key, body, properties,
            mandatory, immediate):
        self.exchange = exchange
        self.routing_key = routing_key
        self.body = body
        self.properties = properties
        self.mandatory = mandatory
        self.immediate = immediate

class IOLoopFake(object):

    def __init__(self, start_callback):
        self.start_callback = start_callback

    def add_timeout(self, deadline, handler):
        raise NotImplementedError

    def remove_timeout(self, timeout_id):
        raise NotImplementedError

    @property
    def poller_type(self):
        raise NotImplementedError

    def start_poller(self):
        raise NotImplementedError

    def update_handler(self, fileno, events):
        raise NotImplementedError
        
    def start(self):
        logging.debug('IPLoop started')
        self.start_callback()

    def stop(self):
        raise NotImplementedError

class ChannelFake(object):

    ### These methods are part of the Fake objects API, do not use
    ### in production code
    
    def __init__(self, connection, on_open_callback=None,
            transport=None):
        self.connection = connection

        self.messages = list()
        self.acked = list()
        self.injected = dict()

        self.consumers = dict()

    def inject(self, queue, header, body):
        if not self.injected.has_key(queue):
            self.injected[queue] = list()

        self.injected[queue].append(dict(header = header, body = body))

    def trigger_consume(self, queue):
        if not self.injected.has_key(queue):
            logging.debug('No messages injected into %s queue, nothing to be done' % queue)
            return

        if len(self.injected[queue]) < 1:
            logging.debug('No messages injected into %s queue, nothing to be done' % queue)
            return

        if not self.consumers.has_key(queue):
            logging.debug('No consumers for %s queue, cannot trigger anything' % queue)
            return

        if len(self.consumers[queue]) < 1:
            logging.debug('No consumers for %s queue, cannot trigger anything' % queue)
            return


        for consumer in self.consumers[queue]:
            for message in self.injected[queue]:
                method = frame.Method(1, spec.Basic.ConsumeOk())
                headers = message['header']
                body = message['body']
                logging.debug('Calling consumer %s with data:\n%s' % 
                        (consumer['callback'], body))
                consumer['callback'](self, method, headers, body)

    ###
    ### These methods are part of the Pika API
    ###

    def add_callback(self, callback, replies):
        raise NotImplementedError

    def add_on_close_callback(self, callback):
        raise NotImplementedError

    def add_on_return_callback(self, callback):
        raise NotImplementedError

    def close(self, code=0, text="Normal Shutdown", from_server=False):
        raise NotImplementedError

    def basic_cancel(self, consumer_tag, nowait=False, callback=None):
        raise NotImplementedError

    def basic_consume(self, consumer_callback, queue='', no_ack=False,
            exclusive=False, consumer_tag=None):
        if not self.consumers.has_key(queue):
            self.consumers[queue] = list()

        self.consumers[queue].append(dict(
                callback = consumer_callback,
                no_ack = no_ack,
                exclusive = exclusive,
                consumer_tag = consumer_tag
                ))

    def basic_publish(self, exchange, routing_key, body, properties=None,
            mandatory=False, immediate=False):
        self.messages.append(PikaMessage(exchange, routing_key, body, 
            properties, mandatory, immediate))

    @property
    def consumer_tags(self):
        raise NotImplementedError

    def flow(self, callback, active):
        raise NotImplementedError

    def exchange_declare(self, callback=None, ticket=0, exchange=None, type='direct',
            passive=False, durable=False, auto_delete=False, internal=False,
            nowait=False, arguments=False):
        raise NotImplementedError

    def exchange_delete(self, callback=None, ticket=0, exchange=None, if_unused=False,
            nowait=False):
        raise NotImplementedError

    def queue_declare(self, callback=None, ticket=0, queue='', passive=False, durable=False, exclusive=False, auto_delete=False, nowait=False, arguments={}):
        raise NotImplementedError

    def queue_bind(self, callback=None, ticket=0, queue='', exchange=None, routing_key='', nowait=False, arguments={}):
        raise NotImplementedError

    def queue_purge(self, callback=None, ticket=0, queue='', nowait=False):
        raise NotImplementedError

    def queue_delete(self, callback=None, ticket=0, queue='', if_unused=False, if_empty=False, nowait=False):
        raise NotImplementedError

    def queue_unbind(self, callback=None, ticket=0, queue='', exchange=None, routing_key='', arguments={}):
        raise NotImplementedError

    def basic_qos(self, callback=None, prefetch_size=0, prefetch_count=0, global_=False):
        raise NotImplementedError

    def basic_get(self, callback=None, ticket=0, queue='', no_ack=False):
        raise NotImplementedError

    def basic_ack(self, delivery_tag=0, multiple=False):
        raise NotImplementedError

    def basic_reject(self, delivery_tag=None, requeue=True):
        raise NotImplementedError

    def basic_recover_async(self, requeue=False):
        raise NotImplementedError

    def basic_recover(self, callback=None, requeue=False):
        raise NotImplementedError

    def tx_select(self, callback=None):
        raise NotImplementedError

    def tx_commit(self, callback=None):
        raise NotImplementedError

    def tx_rollback(self, callback=None):
        raise NotImplementedError


class SelectConnectionFake(object):
    """
    Pretends to be pika.adapters.select_connection.SelectConnection

    Usage:
    >>> connectionfake = SelectConnectionFake()
    >>> FakeConnectionUser(connectionfake)

    This will react like a SelectConnection object but in a blocking manner. It
    will record how it was used for verification later.

    To get the record of usage do:
    >>> record = connectionfake.usage

    To get messages that were published using this fake connection:
    >>> messages = connectionfake.published_messages

    To inject messages and trigger the callbacks for channel.basic_consume():
    >>> connectionfake.inject(header, body)
    >>> connectionfake.trigger_consume()
    """

###
### These methods are part of the Fake objects API, do not
### use them in production code
###

    def __init__(self):
        self.ioloop = IOLoopFake(self.start_callback)
        self._channel = ChannelFake(self)

    @property
    def published_messages(self):
        return self._channel.messages

    def start_callback(self):
        if self.on_open_callback is None:
            return

        logging.debug('calling on_open_callback: %s' % self.on_open_callback.__name__)
        self.on_open_callback(self)

    def inject(self, queue, header, body):
        self._channel.inject(queue, header, body)

    def trigger_consume(self, queue):
        self._channel.trigger_consume(queue)

###
### These methods are part of the Pika API, these can/should be used
### in production code
###
    def __call__(self, parameters=None, on_open_callback=None,
            reconnection_strategy=None):
        logging.debug('SelectConnection initialized')
        self.on_open_callback = on_open_callback
        self.connection_parameters = parameters

        return self

    @property
    def usage(self):
        return self._usage

    def close(self):
        raise NotImplementedError

    @property
    def is_open(self):
        raise NotImplementedError

    def add_on_close_callback(self, callback):
        raise NotImplementedError

    def add_on_open_callback(self, callback):
        raise NotImplementedError

    def add_backpressure_callback(self, callback):
        raise NotImplementedError

    def set_backpressure_multiplier(self, value=0):
        raise NotImplementedError

    def add_timeout(self, delay_sec, callback):
        raise NotImplementedError

    def remove_timeout(self, callback):
        raise NotImplementedError

    def channel(self, on_open_callback, channel_number=None):
        logging.debug("Calling channel's on_open_callback")
        on_open_callback(self._channel)


