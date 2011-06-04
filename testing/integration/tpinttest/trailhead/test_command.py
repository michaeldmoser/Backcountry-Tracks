import unittest

import subprocess
from os import path
from time import sleep
from urllib2 import urlopen, URLError

from tptesting import environment, utils

class TestScript(unittest.TestCase):
    def setUp(self):
        self.environ = environment.create()
        self.environ.make_pristine()
        self.environ.start_rabbitmq()

        subprocess.call(('trailhead', 'start'))

    def tearDown(self):
        self.environ.teardown()

    def test_daemon_start(self):
        """Starting the trailhead daemon should result in a daemonized process"""

        # FIXME: This seems like a horribly unreliable way to test for the existance
        # of a process. There has to be a better way...
        ps = subprocess.Popen(['ps', '-eo', 'args'], stdout=subprocess.PIPE)
        stdout, notused = ps.communicate()
        commands = stdout.splitlines()
        try:
            ret = commands.index('/usr/bin/python /usr/local/bin/trailhead start')
        except ValueError:
            self.fail('trailhead daemon is not running')

    def test_creates_pidfile(self):
        '''Should create a pid'''
        pidfile_path = self.environ.trailhead['pidfile']

        def assert_file_exists():
            assert(path.exists(pidfile_path))

        utils.try_until(0.5, assert_file_exists)

    def test_list_port(self):
        '''Should listen on port 8080 using HTTP'''
        hostname = self.environ.hostname
        url = 'http://%s:8080/' % hostname
        def assert_port_accessable():
            try:
                urlopen(url)
            except URLError, e:
                self.fail(str(e))

        utils.try_until(1, assert_port_accessable)



if __name__ == '__main__':
    unittest.main()

