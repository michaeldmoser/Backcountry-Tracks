from email.parser import Parser

class FakeSMTP(object):

    def __init__(self):
        self.messages = []

    def __call__(self, host='', port=0, local_hostname=None,
            timeout=30):
        self.timeout = timeout
        self.local_hostname = local_hostname
        self.port = port
        self.host = host

        return self

    def sendmail(self, from_addr, to_addrs, msg, mail_options=[], rcpt_options=[]):
        msg = {
                'from': from_addr,
                'to': to_addrs,
                'message': Parser().parsestr(msg)
                }

        self.messages.append(msg)


