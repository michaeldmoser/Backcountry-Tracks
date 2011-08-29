class Daemonizer(object):
    def __init__(self):
        self.daemonized = False

    def __call__(self, pidfile=None, signal_map={}):
        self.pidfile = pidfile
        self.signal_map = signal_map
        return self

    def __enter__(self):
        self.daemonized = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

class PidFile(object):
    def __init__(self, path):
        self.path = path

