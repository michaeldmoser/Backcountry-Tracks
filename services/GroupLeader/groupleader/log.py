
class Logging(object):
    def __init__(self, logging_dictconfig):
        self.logging_dictconfig = logging_dictconfig

    def __call__(self, config):
        self.logging_dictconfig(config['logging'])
