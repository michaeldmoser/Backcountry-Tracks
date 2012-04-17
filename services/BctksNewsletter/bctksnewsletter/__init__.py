from .service import NewsletterSubscriber

class EntryPoint(object):

    def __init__(self, config, env, remoting):
        self.config = config

    def __call__(self):
        return NewsletterSubscriber(self.config)

