import pika
import json

class AdventurerService(object):
    def __init__(self, channel, config, repository):
        self.channel = channel
        self.config = config
        self.repository = repository
    
    def start(self):
        rpc_queue = self.config['queues']['rpc']
        self.channel.basic_consume(self.process_request, queue=rpc_queue)

    def process_request(self, channel, method, header, data):
        request = json.loads(data)
        adventurer_id = request['params'][0]

        properties = pika.BasicProperties(
                content_type = 'application/json',
                correlation_id = header.correlation_id
                )

        adventurer = self.repository.get(adventurer_id)
        self.channel.basic_publish(
                exchange = 'rpc_reply',
                routing_key = header.reply_to,
                properties = properties,
                body = json.dumps(adventurer)
                )


