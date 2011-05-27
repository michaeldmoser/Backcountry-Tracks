import subprocess
import yaml
import os
from os import path

from usertemplate import UserTemplate

class TpEnvironment(object):

    def __init__(self, config):
        self.__config = config

    def __getattr__(self, name):
        if self.__config.has_key(name):
            return self.__config[name]

        users = self.__config['users']
        if users.has_key(name):
            return UserTemplate(users[name])

        raise AttributeError("No attribute: %s" % name)

    def make_pristine(self):
        '''
        Stops all running services and removes all data from the services 
        and generally resets the environment to a clean slate.
        '''
        self.kill_processes()
        self.remove_pid_files()

    def bringup_infrastructure(self):
        '''
        Starts all services which should be running for a functional system
        '''
        self.start_trailhead()

    def teardown(self):
        '''
        Tear down the environment
        '''
        self.kill_processes()
        self.remove_pid_files()

    def start_trailhead(self):
        '''
        Starts the trailhead application server
        '''
        subprocess.call(['trailhead', 'start'])

    def remove_pid_files(self):
        '''
        Removes pid files
        '''
        if path.exists(self.trailhead['pidfile']):
            os.unlink(self.trailhead['pidfile'])

    def kill_processes(self):
        if path.exists(self.trailhead['pidfile']):
            pid = int(open(self.trailhead['pidfile']).read())
            try:
                os.kill(pid, 9)
            except OSError:
                pass

def create():
    # TODO: reading in the config file needs to be cached. Especially for unittesting
    environ_yaml = open('/etc/tptesting.yaml', 'r')
    environ_config = yaml.load(environ_yaml)

    environ = TpEnvironment(environ_config)
    return environ

