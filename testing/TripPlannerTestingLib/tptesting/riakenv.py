import subprocess
import urllib2
import riak
import time

from .utils import wait_for_start

class RiakEnvironment(object):

    def __init__(self, environment):
        self.environ = environment
        self.config = environment.get_config_for('riak')

    def start(self):
        subprocess.call(['/etc/init.d/riak', 'start'], 
                stdout=self.environ.devnull, stderr=self.environ.devnull)
        # wait a few seconds as it seems the first request
        # happening too fast stalls things out for a long period
        # of time
        time.sleep(5) 

        def check_riak_start():
            urllib2.urlopen("http://localhost:8098/riak")
        wait_for_start(check_riak_start, urllib2.URLError)

    def stop(self):
        subprocess.call(['/etc/init.d/riak', 'stop'], 
                stdout=self.environ.devnull, stderr=self.environ.devnull)

        def check_is_stopped():
            try:
                urllib2.urlopen("http://localhost:8098/riak")
            except urllib2.URLError:
                pass
            else:
                raise urllib2.URLError("hasn't stopped yet")
        wait_for_start(check_is_stopped, urllib2.URLError)


    def make_pristine(self):
        subprocess.call(['rm', '-rf', self.config['datadir']],
                stdout=self.environ.devnull, stderr=self.environ.devnull)

    def get_database(self, bucket_name):
        '''
        Returns a Riak bucket instance. bucket_name is the name of the bucket to use
        '''
        client = riak.RiakClient()
        bucket = client.bucket(bucket_name)

        return bucket

