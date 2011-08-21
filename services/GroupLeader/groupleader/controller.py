import yaml
import logging

class GroupLeader(object):
    def __init__(self, config, daemonizer, logging, load_services, setproctitle):
        self.config = config
        self.daemonizer = daemonizer
        self.logging = logging
        self.load_services = load_services
        self.setproctitle = setproctitle

    def run(self):
        pidfile = self.config['pidfile']
        with self.daemonizer(pidfile):
            self.setproctitle('GroupLeader: master')
            self.logging(self.config)
            log = logging.getLogger('top')
            log.debug('GroupLeader is daemonized')
            self.services = self.load_services(self.config)
            self.services.spawn()


