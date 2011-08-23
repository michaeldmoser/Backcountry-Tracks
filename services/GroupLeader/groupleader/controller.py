import logging
import signal
import time

class GroupLeader(object):
    def __init__(self, config, daemonizer, logging, load_services, setproctitle,
            pidlockfile, kill):
        self.config = config
        self.daemonizer = daemonizer
        self.logging = logging
        self.load_services = load_services
        self.setproctitle = setproctitle
        self.pidlockfile = pidlockfile
        self.kill = kill

    def run(self):
        pidfile = self.config['pidfile']
        with self.daemonizer(pidfile, self.shutdown):
            self.logging(self.config)
            logging.debug('GroupLeader about to daemonize')
            logging.debug('GroupLeader daemonized')
            self.setproctitle('GroupLeader: master')
            self.services = self.load_services(self.config)
            self.services.spawn()

# FIXME: Eventually this loop will do something useful such as monitoring 
# for failed processes and restarting them
            while True:
                time.sleep(1)

    def stop(self):
        pid = self.pidlockfile.read_pid()
        self.kill(int(pid), signal.SIGTERM)

    def shutdown(self, pid, stack):
        self.services.shutdown()
        raise SystemExit()




