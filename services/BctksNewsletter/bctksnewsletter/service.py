import logging
from mailsnake import MailSnake

class NewsletterSubscriber(object):

    def __init__(self, config, mailsnake=MailSnake):
        self.mailchimp = MailSnake(config['apikey'])
        self.config = config

    def subscribe(self, user):
        logging.info("Subscribing user to newsletter")
        list_id = self.config.get('list_id')
        if list_id is None:
            raise RuntimeError('No list id was provided in the configuration. Cannot subscribe user to list')

        self.mailchimp.listSubscribe(
                id = list_id,
                email_address = user.get('email'),
                merge_vars = {
                    'FNAME': user.get('first_name'),
                    'LNAME': user.get('last_name'),
                    },
                send_welcome = True
                )

