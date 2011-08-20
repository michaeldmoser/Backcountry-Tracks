
class Daemonizer(object):
    def __init__(self, context_class, pidfile_class):
        self.context_class = context_class
        self.pidfile_class = pidfile_class

    def __call__(self, pidfile_path):
        pidfile = self.pidfile_class(pidfile_path)
        return self.context_class(pidfile=pidfile)

