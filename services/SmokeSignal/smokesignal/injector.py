import pika
import subprocess
import yaml

from smokesignal.application import SmokeSignalApp

CONFIG_PATH = '/etc/tripplanner/tpapp.yaml'

class SmokeSignalFactory():
    def __application(self):
        return SmokeSignalApp

    def __pika_connection(self):
        return pika.BlockingConnection

    def __subprocess(self):
        return subprocess.call

    def __configuration(self):
        config_file = open(CONFIG_PATH, 'r')
        global_config = yaml.load(config_file)
        return global_config['message_routing']

    def __call__(self):
        call = self.__subprocess()
        call(['/etc/init.d/rabbitmq-server', 'start'])

        application = self.__application()
        pika_connection = self.__pika_connection()
        conn_params = pika.ConnectionParameters()

        config = self.__configuration()

        return application(pika_connection = pika_connection(conn_params), config = config)
smokesignal = SmokeSignalFactory()

