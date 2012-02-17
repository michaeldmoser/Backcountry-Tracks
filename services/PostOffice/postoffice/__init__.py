from bctplugins import entrypoint

from .service import EmailService

class EntryPoint(object):

    def __init__(self, config, env, remoting):
        self.config = config

    def __call__(self):
        smtp_config = self.config.get('smtp', {'host': 'localhost', 'port': 25})
        return EmailService(smtp_config)

