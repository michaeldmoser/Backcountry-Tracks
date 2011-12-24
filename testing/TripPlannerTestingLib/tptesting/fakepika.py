"""
Pretends to be pika.adapters.select_connection.SelectConnection

Usage:
>>> connectionfake_class = SelectConnectionFake()
>>> PikaUser(connectionfake_class)

This will react like a SelectConnection object but in a blocking manner. It
will record how it was used for verification later.

To get messages that were published using this fake connection:
>>> message = connectionfake_class.published_messages[0]
>>> assert message.exchange == "example_exchange"
>>> assert message.routing_key == "example.routing.key"
>>> assert message.mandatory
>>> assert message.immediate
>>> assert message.properties == properties
...

"message" in the above case is a tptesting.fakepika.PikaMessage object.

To inject messages and trigger the callbacks for channel.basic_consume():
>>> connectionfake_class.inject(queue_name, header, body)
>>> connectionfake_class.trigger_consume(queue_name)
"""
import logging
import uuid

from pika import frame, spec, exceptions

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

        self.exchanges = dict()
        self.queues = dict()
        self.bindings = list()

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
                method.delivery_tag = 1
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
        self.connection.record_usage(self.basic_consume, consumer_callback, queue=queue,
                no_ack=no_ack, exclusive=exclusive, consumer_tag=consumer_tag)

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
            nowait=False, arguments={}):
        new_exchange = {
                'type': type,
                'passive': passive,
                'durable': durable,
                'auto_delete': auto_delete,
                'internal': internal,
                'nowait': nowait,
                'arguments': arguments
                }
        if self.exchanges.has_key(exchange):
            if new_exchange != self.exchanges[exchange]:
                raise exceptions.AMQPChannelError
        
        self.exchanges[exchange] = new_exchange

    def exchange_delete(self, callback=None, ticket=0, exchange=None, if_unused=False,
            nowait=False):
        raise NotImplementedError

    def queue_declare(self, callback=None, ticket=0, queue='', passive=False, durable=False, exclusive=False, auto_delete=False, nowait=False, arguments={}):
        new_queue = {
                'passive': passive,
                'durable': durable,
                'exclusive': exclusive,
                'auto_delete': auto_delete,
                'nowait': nowait,
                'arguments': arguments,
                }
        if len(queue) < 1:
            queue = str(uuid.uuid4())

        if self.queues.has_key(queue):
            if new_queue != self.queues[queue]:
                raise exceptions.AMQPChannelError

        if callable(callback):
            queue_declare_method = spec.Queue.DeclareOk(queue=queue, message_count=0, consumer_count=0)
            queue_frame = frame.Method(0, queue_declare_method)
            callback(queue_frame)
            

        self.queues[queue] = new_queue

    def queue_bind(self, callback=None, ticket=0, queue='', exchange=None, routing_key='', nowait=False, arguments={}):
        new_binding = {
                'queue': queue,
                'exchange': exchange,
                'routing_key': routing_key,
                'nowait': nowait,
                'arguments': arguments
                }
        self.bindings.append(new_binding)


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
        self.connection.record_usage(self.basic_ack, delivery_tag=delivery_tag, multiple=multiple)

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
        self.on_open_callback = None
        self.ioloop = IOLoopFake(self.start_callback)
        self._channel = ChannelFake(self)
        self.__usage = list()

    @property
    def published_messages(self):
        return self._channel.messages

    @property
    def usage(self):
        return self.__usage

    def start_callback(self):
        self.__usage.append('connected')
        if self.on_open_callback is None:
            return

        logging.debug('calling on_open_callback: %s' % self.on_open_callback.__name__)
        self.on_open_callback(self)

    def inject(self, queue, header, body):
        self._channel.inject(queue, header, body)

    def trigger_consume(self, queue):
        self._channel.trigger_consume(queue)

    def get_exchange_declaration(self, exchange):
        try:
            return self._channel.exchanges[exchange]
        except KeyError:
            return {}

    def get_queue_declaration(self, queue):
        try:
            return self._channel.queues[queue]
        except KeyError:
            return {}

    def get_queues(self):
        return self._channel.queues.keys()

    def get_bindings(self):
        return self._channel.bindings

    def find_binding(self, needle):
        '''
        Searches for the a particular binding and returns it. Returns an empty dict()
        if there is no matching binding.

        @needle should be a dict() with the keys queue, exchange, and routing_key. This
            is what the searching will be based on.
        '''
        bindings = self.get_bindings()

        for binding in bindings:
            binding_match = {
                    'queue': binding['queue'],
                    'exchange': binding['exchange'],
                    'routing_key': binding['routing_key'],
                    }
            if needle == binding_match:
                return binding

        return dict()

    def verify_usage(self, method, args, kwargs):
        '''
        Returns True if method was called and the args and kwargs match the call, 
        otherwise returns False

        method is function object instance on this class
        '''
        for method_call in self.__usage:
            instancemethod = method_call[0]

            if not callable(instancemethod):
                continue

            unbound_method = getattr(instancemethod.im_class, instancemethod.__name__)
            search_unbound_method = getattr(method.im_class, method.__name__)
            if unbound_method == search_unbound_method:
                if args != '*' and method_call[1] != args:
                    return False

                if kwargs != '*' and method_call[2] != kwargs:
                    return False

                return True

        return False

    def was_called(self, method):
        '''
        Returns True if method was called otherwise returns false

        method is function object instance on this class
        '''
        for method_call in self.__usage:
            instancemethod = method_call[0]

            if not callable(instancemethod):
                continue

            unbound_method = getattr(instancemethod.im_class, instancemethod.__name__)
            search_unbound_method = getattr(method.im_class, method.__name__)
            if unbound_method == search_unbound_method:
                return True

        return False

    def record_usage(self, method, *args, **kwargs):
        self.__usage.append((method, args, kwargs))


###
### These methods are part of the Pika API, these can/should be used
### in production code
###
    def __call__(self, parameters=None, on_open_callback=None,
            reconnection_strategy=None):
        logging.debug('SelectConnection initialized')
        self.on_open_callback = on_open_callback
        self.connection_parameters = parameters

        self.__usage.append((self.__init__, (parameters, on_open_callback, reconnection_strategy)))

        return self


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
        self.__usage.append((self.channel, (on_open_callback, channel_number)))
        on_open_callback(self._channel)


class BlockingChannelFake(ChannelFake):

    ###
    ### These methods are part of the Pika API
    ###

    def basic_get(self, ticket=0, queue='', no_ack=False):
        raise NotImplementedError


class BlockingConnectionFake(SelectConnectionFake):
    """
    Pretends to be pika.adapters.select_connection.BlockingConnection

    Usage:
    >>> connectionfake = BlockingConnectionFake()
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
        self._channel = BlockingChannelFake(self)

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
    def __call__(self, parameters=None, reconnection_strategy=None):
        logging.debug('SelectConnection initialized')
        self.connection_parameters = parameters

        return self

    def channel(self, channel_number=None):
        logging.debug("Calling channel's on_open_callback")
        return self._channel
