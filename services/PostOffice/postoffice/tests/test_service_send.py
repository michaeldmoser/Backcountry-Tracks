import unittest

from tptesting import environment
from tptesting.fakesmtplib import FakeSMTP

from postoffice.service import EmailService

class TestServiceConfiguration(unittest.TestCase):
    def setUp(self):
        self.config = {
                'host': 'smtp.example.com',
                'port': 2525,
                'local_hostname': 'backcountrytracks.com',
                'timeout': 31
                }
        self.smtp = FakeSMTP()
        service = EmailService(self.config, smtp=self.smtp)
        service.send('bob@example.com', 'Hello Bob!\nThis is a test');

    def test_connects_to_correct_server(self):
        '''Should connect to the configured SMTP server'''
        self.assertEquals(self.smtp.host, self.config['host'])

    def test_uses_correct_port(self):
        '''Should connect to the SMTP server on the configured port'''
        self.assertEquals(self.smtp.port, self.config['port'])

    def test_uses_correct_local_hostname(self):
        '''Should use the configured local hostname'''
        self.assertEquals(self.smtp.local_hostname, self.config['local_hostname'])

    def test_uses_correct_timeout(self):
        '''Should use the configured local hostname'''
        self.assertEquals(self.smtp.timeout, self.config['timeout'])

class TestServiceConfigDefaults(unittest.TestCase):
    def setUp(self):
        self.smtp = FakeSMTP()
        service = EmailService({}, smtp=self.smtp)
        service.send('bob@example.com', 'Hello Bob!\nThis is a test');

    def test_connects_to_correct_server(self):
        '''Default host configuration should be localhost'''
        self.assertEquals(self.smtp.host, 'localhost')

    def test_uses_correct_port(self):
        '''Default port should be 25'''
        self.assertEquals(self.smtp.port, 25)

    def test_uses_correct_local_hostname(self):
        '''Default local_hostname should be None'''
        self.assertIsNone(self.smtp.local_hostname)

    def test_uses_correct_timeout(self):
        '''Default timeout should be 30'''
        self.assertEquals(self.smtp.timeout, 30)

class TestServiceSending(unittest.TestCase):

    def setUp(self):
        self.smtp = FakeSMTP()
        self.from_ = 'noreply@backcountrytracks.com'
        self.from_line = 'Backcountry Tracks'
        service = EmailService(
                {'from': self.from_, 'from_line': self.from_line},
                smtp=self.smtp
                )
        self.recipient = 'bob@example.com'
        self.message = 'Hello Bob!\nThis is a test'
        self.subject = 'Hi Bob'
        service.send(to=self.recipient, message=self.message, subject=self.subject)

    def test_sends_to_correct_recipient(self):
        '''Should send to the correct recipient'''
        self.assertEquals(self.smtp.messages[0]['to'], [self.recipient])

    def test_uses_from_config(self):
        '''Should use the configured from address'''
        self.assertEquals(self.smtp.messages[0]['from'], self.from_)

    def test_from_line(self):
        '''Should use configured from line'''
        message = self.smtp.messages[0]['message']
        self.assertEquals(self.from_line, message['From'])

    def test_to_line(self):
        '''Should use configured from line'''
        message = self.smtp.messages[0]['message']
        self.assertEquals(self.recipient, message['To'])

    def test_subject(self):
        '''Should use passed in subject'''
        message = self.smtp.messages[0]['message']
        self.assertEquals(self.subject, message['Subject'])





if __name__ == '__main__':
    unittest.main()

