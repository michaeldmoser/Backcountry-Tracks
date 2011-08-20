class Service(object):
    def __init__(self, entry_point, config, environ):
        self.entry_point = entry_point
        self.config = config
        self.environ = environ

    def __call__(self):
        self.entry_point(self.config, self.environ).start()

class ServiceBuilder(object):
    def __init__(self, load_entry_point, group, Service, Process, environ):
        self.load_entry_point = load_entry_point
        self.group = group
        self.Service = Service
        self.Process = Process
        self.environ = environ

    def __call__(self, dist, name, config):
        entry_point = self.load_entry_point(dist, self.group, name)
        service = self.Service(entry_point, config, self.environ)
        return self.Process(target=service)

class Services(object):
    def __init__(self, load_service):
        self.load_service = load_service
        self.services = list()

    def __call__(self, config):
        self.config = config
        for service, config in self.config['services'].items():
            dist, name = service.split('/')
            service = self.load_service(dist, name, config)
            self.services.append(service)
        return self

    def spawn(self):
        for service in self.services:
            service.start()
