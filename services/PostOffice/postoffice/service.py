import logging

from smtplib import SMTP
from email.mime.text import MIMEText

class EmailService(object):

    def __init__(self, config, smtp=SMTP):
        self.config = config
        self.smtp = smtp

    def __get_smtp_config(self):
        config = {
                'host': self.config.get('host', 'localhost'),
                'port': self.config.get('port', 25),
                'local_hostname': self.config.get('local_hostname'),
                'timeout': self.config.get('timeout', 30)
                }
        return config

    def send(self, to=None, message=None, subject=None):
        stmp = self.smtp(**self.__get_smtp_config())        
        from_ = self.config.get('from', 'noreply@localhost')
        from_line = self.config.get('from_line')
        logging.debug("From header is: %s" % from_line)

        email = MIMEText(message)
        email['From'] = from_line
        email['To'] = to
        email['Subject'] = subject

        logging.debug('Sending email message:\n=============================================\n%s\n=============================================' % str(email))
        stmp.sendmail(from_, [to], email.as_string())
