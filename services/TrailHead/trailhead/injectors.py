from daemon import DaemonContext
from lockfile.pidlockfile import PIDLockFile

from tornado.web import Application
import tornado.ioloop

import pika
from pika.adapters.tornado_connection import TornadoConnection

from trailhead.register import RegisterHandler
from trailhead.mq import PikaClient

from trailhead.server import TrailHead


def application():
    mq_params = pika.ConnectionParameters(host = 'localhost')
    mqclient = PikaClient(TornadoConnection, mq_params)

    pidfile = PIDLockFile("/var/run/tripplanner/trailhead.pid")

    trailhead = TrailHead(
        daemonizer = DaemonContext,
        ioloop = tornado.ioloop,
        webapp = Application,
        mqclient = mqclient,
        pidfile = pidfile
        )

    return trailhead
