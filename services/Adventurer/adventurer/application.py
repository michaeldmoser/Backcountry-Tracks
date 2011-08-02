import uuid

class Application(object):
    def __init__(self, bucket=None, mailer=None,
            trailhead_url='http://www.backcountrytracks.com/app'):
        self.bucket = bucket
        self.mailer = mailer
        self.trailhead_url = trailhead_url

        def generate_confirmation_key():
            return str(uuid.uuid4())

        self.generate_confirmation_key = generate_confirmation_key

    def register(self, data):
        '''
        Registers a new adventurer with the system by saving it to the database
        and sends an email to the user for completing the registration
        '''
        email = str(data['email'])
        confirmation_key = self.generate_confirmation_key()
        data['confirmation_key'] = confirmation_key

        new_registration = self.bucket.new(email, data = data)
        new_registration.store()

        self.send_complete_registration_email(
                email,
                data['first_name'],
                data['last_name'],
                confirmation_key
                )

    def generate_confirmation_key(self):
        return str(uuid.uuid4())

    def send_complete_registration_email(self, email, first_name, last_name, confirmation_key):
        '''
        Sends a registration confirmation message to user with a link to complete registration
        '''
        from_address = 'noreply@example.org'
        from_line = 'BackCountryTracks Registration'
        subject = 'BackCountryTracks Registration'
        body = self._build_complete_registration_email_body(
                email,
                first_name,
                last_name,
                confirmation_key
                )

        self.mailer.send(from_address, from_line, email, subject, body)

    def _build_complete_registration_email_body(self, email, first_name, last_name, confirmation_key):
        output = []
        message = "%s %s, welcome to BackCountryTracks.com!" \
            "To complete your registration, click on the link below or copy and paste it into your browser's location bar." \
            "Once you have completed your registration, you can login to your BackCountryTracks.com account!" % (first_name, last_name)

        href = u'%s?email=%s&confirmation_key=%s' % (self.trailhead_url, email, confirmation_key)
        link = u'<a href="%s">%s</a>' % (href, href)

        output.append(u'<html><head><title>Welcome to BackCountryTracks.com!</title></head><body>')
        output.append(u'<p>%s</p>' % message)
        output.append(u'<p>%s</p>' % link)
        output.append(u'</body></html>')
        return '\r\n'.join(output)

    def login(self, email, password):
        '''
        Validates user crendentials and returns true if the email/password combination exists
        '''
        user_object = self.bucket.get(str(email))
        user = user_object.get_data()
        if user and user['password'] == str(password):
            return True
        else:
            return False
