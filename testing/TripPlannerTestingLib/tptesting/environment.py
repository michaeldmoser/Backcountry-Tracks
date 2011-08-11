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
from .nginx import NginxEnvironment
from .trailhead import TrailheadEnvironment
from .gear import Gear

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
        self.nginx = NginxEnvironment(self)
        self.trailhead = TrailheadEnvironment(self)

        self.gear = Gear(self)

        logging.config.dictConfig(default_logging_config)

    def __getattr__(self, name):
        if self.__config.has_key(name):
            return self.__config[name]

        users = self.__config['users']
        if users.has_key(name):
            user = UserTemplate(users[name])
            user.set_trailhead_url(self.trailhead_url)
            return user

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
        self.nginx.start()
        self.rabbitmq.start()
        self.riak.start()
        self.adventurer.start()
        self.trailhead.start()

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
        self.trailhead.remove_pidfile()
        self.adventurer.remove_pidfile()

    def kill_processes(self):
        '''
        Shutdowns all services
        '''
        self.trailhead.stop()
        self.adventurer.stop()
        self.riak.stop()
        self.rabbitmq.stop()
        self.nginx.stop()

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

