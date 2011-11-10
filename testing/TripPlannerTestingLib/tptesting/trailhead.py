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


