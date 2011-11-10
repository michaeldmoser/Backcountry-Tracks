import traceback

import logging
log = logging.getLogger('top')

class Service(object):
    def __init__(self, dist, name, entry_point, config, environ, setproctitle):
        log.debug('Created service for %s' % str(entry_point))
        self.entry_point = entry_point
        self.config = config
        self.environ = environ
        self.name = name
        self.dist = dist
        self.setproctitle = setproctitle

    def __call__(self):
        try:
            log.debug('Start service: %s/%s' % (self.dist, self.name))
            self.setproctitle('GroupLeader: %s/%s' % (self.dist, self.name))
            self.entry_point(self.config, self.environ).start()
            log.debug('Process (%s/%s) finished' % (self.dist, self.name))
        except Exception:
            trace_back = traceback.format_exc()
            log.error(trace_back)
            raise


class ServiceBuilder(object):
    def __init__(self, load_entry_point, group, Service, Process, environ, setproctitle):
        self.load_entry_point = load_entry_point
        self.group = group
        self.Service = Service
        self.Process = Process
        self.environ = environ
        self.setproctitle = setproctitle

    def __call__(self, dist, name, config):
        log.debug("Loading entry point: %s, %s, %s" % (dist, self.group, name))
        entry_point = self.load_entry_point(dist, self.group, name)
        service = self.Service(dist, name, entry_point, config,
                self.environ, self.setproctitle)
        return self.Process(target=service)

class Services(object):
    def __init__(self, load_service):
        self.load_service = load_service
        self.services = list()

    def __call__(self, config):
        self.config = config
        for service, config in self.config['services'].items():
            try:
                dist, name = service.split('/')
                service = self.load_service(dist, name, config)
                self.services.append(service)
            except Exception:
                trace_back = traceback.format_exc()
                log.error("Error with %s/%s server:\n%s" % (dist, name, trace_back))
                raise
        return self

    def spawn(self):
        for service in self.services:
            service.start()

    def shutdown(self):
        for service in self.services:
            service.terminate()
