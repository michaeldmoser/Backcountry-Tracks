from tornado.web import Application
import tornado.ioloop

import pika
from pika.adapters.tornado_connection import TornadoConnection

from bctmessaging.remoting import RemotingClient

from trailhead.mq import PikaClient
from trailhead.server import TrailHead


class EntryPoint(object):

    def __init__(self, config, environ):
        self.config = config
        self.environ = environ

    def start(self):
        mq_params = pika.ConnectionParameters(host = 'localhost')
        mqclient = PikaClient(TornadoConnection, mq_params, RemotingClient)

        self.trailhead = TrailHead(
                ioloop = tornado.ioloop,
                webapp = Application,
                mqclient = mqclient,
                environ = self.environ,
                config = self.config
                )
        self.trailhead.run()

