import smtplib
import socket

class Mailer(object):

    def __init__(self, host='localhost', port=25):
        self.host = host
        self.port = port
        self.smtp = smtplib.SMTP()

    def send(self, from_address, from_line, to, subject, body):

        headers = self._build_headers(from_line, to, subject)
        message = u'\r\n\r\n'.join((headers, body))

        if type(message) == unicode:
            message = message.encode('utf-8')

        self.smtp.connect(self.host, self.port)
        self.smtp.sendmail(from_address, to, message)
        self.smtp.quit()

    def _build_headers(self, from_line, to, subject):
        headers = []
        headers.append('From: %s' % from_line)
        headers.append('Subject: %s' % subject)
        headers.append('To: %s' % to)
        headers.append('Content-Type: text/html')

        return '\r\n'.join(headers)
