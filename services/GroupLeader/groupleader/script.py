from .controller import GroupLeader

SERVICES_ENTRY_POINT_GROUP = 'tripplanner.service'
CONFIG_PATH = '/etc/tripplanner/config.yaml'

def build_daemonizer():
    from daemon import DaemonContext
    from lockfile.pidlockfile import PIDLockFile
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
            Service, Process, environ)

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

    gl = GroupLeader(config, daemonizer, logging, load_services)
    gl.run()

