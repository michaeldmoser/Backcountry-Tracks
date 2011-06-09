import subprocess

def parse_bool_string(string):
    return True if string == 'true' else False

class RabbitMQEnvironment(object):

    def __init__(self, environment):
        self.environ = environment
        self.devnull = self.environ.devnull

    def make_pristine(self):
        '''
        Resets RabbitMQ exchange, queue, and binding information to factory settings
        '''
        self.start()
        self.reset()
        self.stop()

    def stop_app(self):
        '''
        Runs rabbitmqctl stop_app
        '''
        subprocess.call(['rabbitmqctl', 'stop_app'], stdout=self.devnull,
                stderr=self.devnull)

    def reset(self):
        '''
        Runs rabbitmqctl reset. stops the app, resets, then starts app
        '''
        self.stop_app()
        subprocess.call(['rabbitmqctl', 'reset'], stdout=self.devnull,
                stderr=self.devnull)
        self.start_app()

        
    def start_app(self):
        '''
        Runs rabbitmqctl start_app
        '''
        subprocess.call(['rabbitmqctl', 'start_app'], stdout=self.devnull,
                stderr=self.devnull)

    def start(self):
        '''
        Starts the rabbitmq server by running smokesignal
        '''
        subprocess.call(['smokesignal', 'start'], 
                stdout=self.devnull, stderr=self.devnull)

    def stop(self):
        '''
        Stops the rabbitmq server
        '''
        subprocess.call(['/etc/init.d/rabbitmq-server', 'stop'], 
                stdout=self.devnull, stderr=self.devnull)

    def start_server(self):
        '''
        Starts the rabbitmq server directly
        '''
        subprocess.call(['/etc/init.d/rabbitmq-server', 'start'], 
                stdout=self.devnull, stderr=self.devnull)


    def list_exchanges(self):
        '''
        Returns a dict() keyed on the exchange name. The value is a dict():
          @type The queue type (direct, topic, fanout)
          @durable The exchanges durability (True, False)
          @auto_delete Whether to auto delete the exchange (True, False)
          @internal Is the exchange internal (True, False)
          @arguments The arguments of the exchange (a string)
        '''
        args = ['name', 'type', 'durable', 'auto_delete', 'internal', 'arguments']
        command = ['rabbitmqctl', 'list_exchanges']
        command.extend(args)
        list_exchanges = (subprocess.check_output(command)).strip()
        list_exchanges_lines = list_exchanges.split('\n')
        list_exchanges_split = [exchange_line.split('\t') for exchange_line in list_exchanges_lines]

        exchanges_trimmed = list_exchanges_split[1:-1]
        exchanges = dict()
        for exchange in exchanges_trimmed:
            name, exchange_type, durable, auto_delete, internal, arguments = exchange
            exchanges[name] = {
                    'type': exchange_type,
                    'durable': parse_bool_string(durable),
                    'auto_delete': parse_bool_string(auto_delete),
                    'internal': parse_bool_string(internal),
                    'arguments': arguments,
                    }

        return exchanges

    def list_queues(self):
        '''
        Lists the rabbitmq queues

        Returns a dict() keyed on the exchange name. The value is a dict():
          @durable The queues durability (True, False)
          @auto_delete Whether to auto delete the queue (True, False)
          @arguments The arguments of the queue (a string)
        '''
        command = ['rabbitmqctl', 'list_queues', 'name', 'durable', 
                'auto_delete', 'arguments']
        list_queues_output = (subprocess.check_output(command)).strip()
        list_queues_lines = list_queues_output.split('\n')
        queues_list = [queue.split('\t') for queue in list_queues_lines]
        queues_trimmed = queues_list[1:-1]
        queues = dict()
        for queue in queues_trimmed:
            name, durable, auto_delete, arguments = queue
            queues[name] = {
                    'durable': parse_bool_string(durable),
                    'auto_delete': parse_bool_string(auto_delete),
                    'arguments': arguments
                    }

        return queues

    def list_bindings(self):
        '''
        Lists the rabbitmq bindings

        Returns a list() of dict()'s. The dict() has the following keys/values
             @source_name Name of the source of the binding
             @source_kind Type of source (exchange, queue)
             @destination_name Name of the destination
             @destination_kind Type of destination (exchange, queue)
             @routing_key The routing key for this binding
             @arguments Any arguments used to create the binding
        '''
        command = ['rabbitmqctl', 'list_bindings', 'source_name', 'source_kind',
                'destination_name', 'destination_kind', 'routing_key',
                'arguments']
        list_bindings_output = (subprocess.check_output(command)).strip()
        list_bindings_lines = list_bindings_output.split('\n')
        bindings_untrimmed = [binding.split('\t') for binding in list_bindings_lines]
        bindings_list = bindings_untrimmed[1:-1]

        bindings = []
        for binding in bindings_list:
            source_name, source_kind, destination_name, destination_kind, routing_key, arguments = binding
            bindings.append({
                'source_name': source_name,
                'source_kind': source_kind,
                'destination_kind': destination_kind,
                'destination_name': destination_name,
                'routing_key': routing_key,
                'arguments': arguments,
                })

        return bindings


