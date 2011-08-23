import sys
from .controller import GroupLeader
from setproctitle import setproctitle
from lockfile.pidlockfile import PIDLockFile
from os import kill

SERVICES_ENTRY_POINT_GROUP = 'tripplanner.service'
CONFIG_PATH = '/etc/tripplanner/tpapp.yaml'

def build_daemonizer():
    from daemon import DaemonContext
    from .daemonizer import Daemonizer

    return Daemonizer(DaemonContext, PIDLockFile)

def build_load_services(config):
    from .services import Services, ServiceBuilder, Service
    from .environment import Environment, MessagingBuilder
    from pkg_resources import load_entry_point
    from multiprocessing import Process

    messaging = MessagingBuilder(config)
    environ = Environment(config, messaging)
    load_service = ServiceBuilder(load_entry_point, SERVICES_ENTRY_POINT_GROUP,
            Service, Process, environ, setproctitle)

    return Services(load_service)

def build_logging():
    from logging.config import dictConfig
    from .log import Logging

    return Logging(dictConfig)


def load_config():
    import yaml
    config_file = open(CONFIG_PATH)
    return yaml.load(config_file)

def main():
    config = load_config()
    daemonizer = build_daemonizer()
    load_services = build_load_services(config)
    logging = build_logging()

    pidlockfile = PIDLockFile(config['pidfile'])

    gl = GroupLeader(config, daemonizer, logging, load_services, setproctitle,
            pidlockfile, kill)

    if len(sys.argv) < 2:
        raise RuntimeError("You must specify start or stop")

    if sys.argv[1] == 'start':
        gl.run()
    elif sys.argv[1] == 'stop':
        gl.stop()
    else:
        raise RuntimeError("You must specify start or stop")


