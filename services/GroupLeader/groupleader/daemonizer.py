import signal

class Daemonizer(object):
    def __init__(self, context_class, pidfile_class):
        self.context_class = context_class
        self.pidfile_class = pidfile_class

    def __call__(self, pidfile_path, sigterm_handler):
        pidfile = self.pidfile_class(pidfile_path)
        sig_map = {
                signal.SIGTTIN: None,
                signal.SIGTTOU: None,
                signal.SIGTSTP: None,
                signal.SIGTERM: sigterm_handler
                }
        return self.context_class(pidfile=pidfile, signal_map=sig_map)

