import subprocess

class NginxEnvironment(object):

    def __init__(self, environment):
        self.environ = environment
        self.devnull = self.environ.devnull

    def start(self):
        '''
        Start nginx
        '''
        subprocess.call(['/etc/init.d/nginx', 'start'], stdout=self.devnull,
                stderr=self.devnull)

    def stop(self):
        '''
        Stop nginx
        '''
        subprocess.call(['/etc/init.d/nginx', 'stop'], stdout=self.devnull,
                stderr=self.devnull)
