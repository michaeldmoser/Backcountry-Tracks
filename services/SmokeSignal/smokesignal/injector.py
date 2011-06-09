import pika
import subprocess

from smokesignal.application import SmokeSignalApp

class SmokeSignalFactory():
    def __application(self):
        return SmokeSignalApp

    def __pika_connection(self):
        return pika.BlockingConnection

    def __subprocess(self):
        return subprocess.call

    def __call__(self):
        call = self.__subprocess()
        call(['/etc/init.d/rabbitmq-server', 'start'])

        application = self.__application()
        pika_connection = self.__pika_connection()
        conn_params = pika.ConnectionParameters()

        return application(pika_connection = pika_connection(conn_params))
smokesignal = SmokeSignalFactory()

