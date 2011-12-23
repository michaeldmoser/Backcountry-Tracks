import unittest

import json
import uuid
import pika
import mailbox

from tptesting import environment, utils

class InviteAFriendEmails(unittest.TestCase):
    def test_sends_email(self):
        environ = environment.create()
        environ.make_pristine()
        environ.bringup_infrastructure()

        body = {
                'jsonrpc': '2.0',
                'method': 'send',
                'id': str(uuid.uuid4()),
                'params': {
                    'to': environ.ramona.email,
                    'message': 'Hello Ramona'
                    }
                }

        environ.rabbitmq.publish_message(routing_key='rpc.email', body=body)

        def check_email():
            mbox_path = environ.get_config_for('mbox_file')
            mbox = mailbox.mbox(mbox_path)

            for message in mbox.values():
                if body['params']['to'] in message.get('To'):
                    return

            self.fail('Could not find a message addressed to %s' % body['params']['to'])
        utils.try_until(2, check_email)

if __name__ == '__main__':
    unittest.main()
