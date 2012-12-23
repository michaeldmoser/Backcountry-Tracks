import traceback

import logging
log = logging.getLogger('top')

class ProcessController(object):
    def __init__(self, dist, name, entry_point, config, environ, setproctitle, process_name):
        log.debug('Created process for %s' % str(entry_point))
        self.entry_point = entry_point
        self.config = config
        self.environ = environ
        self.name = name
        self.dist = dist
        self.setproctitle = setproctitle
        self.process_name = process_name

    def __call__(self):
        try:
            log.debug('Start process: %s' % self.process_name)
            self.setproctitle('GroupLeader: %s' % self.process_name)
            self.entry_point(self.config, self.environ).start()
            log.debug('Process (%s/%s) finished' % (self.dist, self.name))
        except Exception:
            trace_back = traceback.format_exc()
            log.error(trace_back)
            raise


class ProcessBuilder(object):
    def __init__(self, group, ControllerClass, Process, environ, setproctitle):
        self.group = group
        self.ControllerClass = ControllerClass
        self.Process = Process
        self.environ = environ
        self.setproctitle = setproctitle

    def __call__(self, dist, name, config, process_name):
        logging.debug("Loading entry point: %s, %s, %s" % (dist, self.group, name))
        entry_point = self.environ.get_component(self.group, dist, name)
        service = self.ControllerClass(dist, name, entry_point, config,
                self.environ, self.setproctitle, process_name)
        return self.Process(target=service)

class Processes(object):
    def __init__(self, load_service):
        self.load_service = load_service
        self.services = list()

    def __call__(self, config):

        self.config = config
        logging.debug('Start loading processes %s', self.config['processes'])

        for service in self.config['processes']:
            config_name = service['name']
            entrypoint = service['entrypoint']
            logging.warn('Loading service %s ', config_name)
            service_config = self.config[config_name]
            try:
                dist, name = service['entrypoint'].split('/')
                service = self.load_service(dist, name, service_config, config_name)
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

