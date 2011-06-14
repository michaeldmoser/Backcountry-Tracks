import subprocess
import yaml
import os
import time
from os import path
import urllib2

import logging
import logging.config

from usertemplate import UserTemplate
import riak

import subprocess

from .adventurer import AdventurerEnvironment
from .riakenv import RiakEnvironment
from .utils import wait_for_start
from .rabbitmq import RabbitMQEnvironment

default_logging_config = {
        'version': 1,
        'formatters': {
            'simple': {
                'format': "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
        'handlers': {
            'main': {
                'class': 'tptesting.tplogging.MemoryLoggingHandler',
                'level': 'DEBUG',
                'formatter': 'simple',
                },
            },
        'loggers': {
            'main_logger': {
                'level': 'DEBUG',
                'handlers': ['main'],
                'propagate': 'no',
                },
            },
        'root': {
            'level': 'DEBUG',
            'handlers': ['main'],
            },
        }


class TpEnvironment(object):

    def __init__(self, config):
        self.__config = config
        self.devnull = open('/dev/null', 'a')

        self.adventurer = AdventurerEnvironment(self)
        self.riak = RiakEnvironment(self)
        self.rabbitmq = RabbitMQEnvironment(self)

        logging.config.dictConfig(default_logging_config)

    def __getattr__(self, name):
        if self.__config.has_key(name):
            return self.__config[name]

        users = self.__config['users']
        if users.has_key(name):
            return UserTemplate(users[name])

        raise AttributeError("No attribute: %s" % name)

    def get_config_for(self, service):
        '''Retrieves a section of the tptesting.yaml file'''
        return self.__config[service]

    def make_pristine(self):
        '''
        Stops all running services and removes all data from the services 
        and generally resets the environment to a clean slate.
        '''
        self.kill_processes()
        self.remove_pid_files()

        self.rabbitmq.make_pristine()
        self.adventurer.make_pristine()
        self.riak.make_pristine()

    def bringup_infrastructure(self):
        '''
        Starts all services which should be running for a functional system
        '''
        self.rabbitmq.start()
        self.riak.start()
        self.adventurer.start()
        self.start_trailhead()

    def teardown(self):
        '''
        Tear down the environment
        '''
        self.kill_processes()
        self.remove_pid_files()

    def remove_pid_files(self):
        '''
        Removes pid files
        '''
        if path.exists(self.trailhead['pidfile']):
            os.unlink(self.trailhead['pidfile'])

        self.adventurer.remove_pidfile()

    def kill_processes(self):
        '''
        Shutdowns all services
        '''
        self.stop_trailhead()
        self.adventurer.stop()
        self.riak.stop()
        self.rabbitmq.stop()

    def start_trailhead(self):
        '''
        Starts the trailhead application server
        '''
        subprocess.call(['trailhead', 'start'], 
                stdout=self.devnull, stderr=self.devnull)
        def check_trailhead_start():
            urllib2.urlopen("http://localhost:8080/")
        wait_for_start(check_trailhead_start, urllib2.URLError)

    def stop_trailhead(self):
        '''
        Stop the trailhead app server
        '''
        if path.exists(self.trailhead['pidfile']):
            pid = int(open(self.trailhead['pidfile']).read())
            try:
                os.kill(pid, 9)
            except OSError:
                pass

    def create_user(self, user):
        adventurers = self.riak.get_database('adventurers')
        adventurer = adventurers.new(user.email, data=user)
        adventurer.store()


def create():
    # TODO: reading in the config file needs to be cached. Especially for unittesting
    environ_yaml = open('/etc/tptesting.yaml', 'r')
    environ_config = yaml.load(environ_yaml)

    environ = TpEnvironment(environ_config)
    return environ

