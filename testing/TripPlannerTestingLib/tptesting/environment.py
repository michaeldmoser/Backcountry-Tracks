import subprocess
import yaml
import os
import time
from os import path
import urllib2

from usertemplate import UserTemplate
import riak

def wait_for_start(check_if_started, exception_class):
    '''
    Repeatedly call check_if_started for upto 10 seconds. check_if_started 
    should raise and exception exception_class which will be caught. If
    either the 10 seconds has elapsed or an exception that is not exception_class
    is raised this function will fail.
    '''

    current_time = 0
    for timed in range(10):
        try:
            check_if_started()
        except exception_class:
            time.sleep(0.1)
            current_time += 0.1

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
        self.start_rabbitmq()
        self.start_riak()
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

    def kill_processes(self):
        '''
        Shutdowns all services
        '''
        self.stop_trailhead()
        self.stop_riak()
        self.stop_rabbitmq()

    def start_rabbitmq(self):
        '''
        Starts the rabbitmq server
        '''
        subprocess.call(['/etc/init.d/rabbitmq-server', 'start'])

    def stop_rabbitmq(self):
        '''
        Stops the rabbitmq server
        '''
        subprocess.call(['/etc/init.d/rabbitmq-server', 'stop'])

    def start_trailhead(self):
        '''
        Starts the trailhead application server
        '''
        subprocess.call(['trailhead', 'start'])
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

    def start_riak(self):
        '''
        Start the riak server
        '''
        subprocess.call(['/etc/init.d/riak', 'start'])
        def check_riak_start():
            urllib2.urlopen("http://localhost:8089/")
        wait_for_start(check_riak_start, urllib2.URLError)

    def stop_riak(self):
        '''
        Stop the riak server
        '''
        subprocess.call(['/etc/init.d/riak', 'stop'])

    def get_database(self, bucket_name):
        '''
        Returns a Riak bucket instance. bucket_name is the name of the bucket to use
        '''
        client = riak.RiakClient()
        bucket = client.bucket(bucket_name)

        return bucket


def create():
    # TODO: reading in the config file needs to be cached. Especially for unittesting
    environ_yaml = open('/etc/tptesting.yaml', 'r')
    environ_config = yaml.load(environ_yaml)

    environ = TpEnvironment(environ_config)
    return environ

