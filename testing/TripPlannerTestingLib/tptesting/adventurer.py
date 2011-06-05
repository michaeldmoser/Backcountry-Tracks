import subprocess
from os import path
import os

class AdventurerEnvironment(object):
    def __init__(self, environment):
        self.environment = environment
        self.config = self.environment.get_config_for('adventurer')

    def start(self):
        subprocess.check_call(self.config['start'], stdout=self.environment.devnull, 
                stderr=self.environment.devnull)

    def stop(self):
        if not path.exists(self.config['pidfile']):
            return

        pid = open(self.config['pidfile'], 'r').read()
        os.kill(int(pid), 9)

# comming soon...
        #subprocess.check_call(self.config['stop'], stdout=self.environment.devnull, 
        #        stderr=self.environment.devnull)

    def make_pristine(self):
        self.stop()

    def remove_pidfile(self):
        if not path.exists(self.config['pidfile']):
            return

        os.unlink(self.config['pidfile'])



