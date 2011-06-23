class Daemonizer(object):
    def __init__(self):
        self.daemonized = False

    def __call__(self, pidfile=None):
        self.pidfile = pidfile
        return self

    def __enter__(self):
        self.daemonized = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

class PidFile(object):
    pass

