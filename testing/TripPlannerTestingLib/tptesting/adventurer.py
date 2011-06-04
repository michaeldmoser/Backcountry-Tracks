import subprocess
from os import path

class AdventurerEnvironment(object):
    def __init__(self, environment):
        self.environment = environment
        self.config = self.environment.get_config_for('adventurer')

    def start(self):
        subprocess.check_call(self.config['start'], stdout=self.environment.devnull, 
                stderr=self.environment.devnull)

    def stop(self):
        subprocess.check_call(self.config['stop'], stdout=self.environment.devnull, 
                stderr=self.environment.devnull)

    def make_pristine(self):
        self.stop()

