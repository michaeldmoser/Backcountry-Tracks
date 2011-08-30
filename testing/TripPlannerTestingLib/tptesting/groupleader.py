import subprocess
from os import path
import os

class GroupLeaderEnvironment(object):
    def __init__(self, environment):
        self.environment = environment
        self.config = self.environment.get_config_for('groupleader')

    def start(self):
        subprocess.check_call(self.config['start'], stdout=self.environment.devnull,
                stderr=self.environment.devnull)

    def stop(self):
        subprocess.call(self.config['stop'], stdout=self.environment.devnull,
                stderr=self.environment.devnull)

    def remove_pidfile(self):
        if not path.exists(self.config['pidfile']):
            return

        os.unlink(self.config['pidfile'])

