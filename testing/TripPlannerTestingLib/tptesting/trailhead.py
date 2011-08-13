import subprocess
from os import path
import os
import urllib2

from tptesting.utils import wait_for_start

class TrailheadEnvironment(object):
    def __init__(self, environment):
        self.environ = environment
        self.devnull = self.environ.devnull
        self.config = self.environ.get_config_for('trailhead')

    def make_pristine(self):
        self.stop()

    def stop(self):
        if path.exists(self.config['pidfile']):
            pid = int(open(self.config['pidfile']).read())
            try:
                os.kill(pid, 9)
            except OSError:
                pass

    def reset(self):
        pass

    def start(self):
        subprocess.call(['trailhead', 'start'], 
                stdout=self.devnull, stderr=self.devnull)
        def check_trailhead_start():
            urllib2.urlopen("http://localhost:8080/")
        wait_for_start(check_trailhead_start, urllib2.URLError)

    def remove_pidfile(self):
        if path.exists(self.config['pidfile']):
            os.unlink(self.config['pidfile'])


