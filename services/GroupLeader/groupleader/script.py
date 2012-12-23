import sys
from .controller import GroupLeader
from setproctitle import setproctitle
from lockfile.pidlockfile import PIDLockFile
from os import kill

from bctks.environment import BcTksEnvironment
from bctks.processes import ProcessController, ProcessBuilder, Processes

SERVICES_ENTRY_POINT_GROUP = 'tripplanner.service'
CONFIG_PATH = '/etc/tripplanner/tpapp.yaml'

def build_daemonizer():
    from daemon import DaemonContext
    from .daemonizer import Daemonizer

    return Daemonizer(DaemonContext, PIDLockFile)

def build_load_processes(config):
    from multiprocessing import Process

    environ = BcTksEnvironment(config)
    load_process = ProcessBuilder(SERVICES_ENTRY_POINT_GROUP,
            ProcessController, Process, environ, setproctitle)

    return Processes(load_process)

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
    load_processes = build_load_processes(config)
    logging = build_logging()

    pidlockfile = PIDLockFile(config['pidfile'])

    gl = GroupLeader(config, daemonizer, logging, load_processes, setproctitle,
            pidlockfile, kill)

    if len(sys.argv) < 2:
        raise RuntimeError("You must specify start or stop")

    if sys.argv[1] == 'start':
        gl.run()
    elif sys.argv[1] == 'stop':
        gl.stop()
    else:
        raise RuntimeError("You must specify start or stop")


