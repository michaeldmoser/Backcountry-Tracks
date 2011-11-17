import uuid
import logging
log = logging.getLogger('Adventurer2/service')

from bctservices.crud import BasicCRUDService
from .forms import LoginForm, RegisterForm

class AdventurerRepository(BasicCRUDService):

    def __init__(self,
            bucket_name = 'adventurers',
            mailer = None,
            db = None,
            trailhead_url = 'http://www.backcountrytracks.com/app'
            ):
        self.riak = db
        self.bucket_name = bucket_name
        self.bucket = self.riak.bucket(bucket_name)
        self.trailhead_url = trailhead_url
        self.mailer = mailer

    def register(self, **data):
        '''
        Registers a new adventurer with the system by saving it to the database
        and sends an email to the user for completing the registration
        '''
        form = RegisterForm(**data)
        if not form.validate():
            log.debug('Failed form validation: %s' % str(form.errors))
            result = {'successful': False, 'messages': form.errors}
            return result

        clean_data = form.data
        email = str(clean_data['email'])
        confirmation_key = self.generate_confirmation_key()
        clean_data['confirmation_key'] = confirmation_key

        #check that the user isn't already in the system
        user_object = self.bucket.get(email)
        user = user_object.get_data()
        if user:
            log.debug('Duplicate registration for %s' % user['email'])
            result = {'successful': False, 'messages': {
                'form': ['This email address has already been registered.']
                }}
            return result

        new_registration = self.bucket.new(email, data = clean_data)
        new_registration.store()

        self.send_complete_registration_email(
                email,
                clean_data['first_name'],
                clean_data['last_name'],
                confirmation_key
                )

        log.debug('Completed registration for %s' % email)
        result = {'successful': True}
        return result

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

        href = u'%s/activate/%s/%s' % (self.trailhead_url, email, confirmation_key)
        link = u'<a href="%s">%s</a>' % (href, href)

        output.append(u'<html><head><title>Welcome to BackCountryTracks.com!</title></head><body>')
        output.append(u'<p>%s</p>' % message)
        output.append(u'<p>%s</p>' % link)
        output.append(u'</body></html>')
        return '\r\n'.join(output)

    def login(self, email='', password=''):
        '''
        Validates user crendentials and returns true if the email/password combination exists
        '''
        form = LoginForm(email = email, password = password)
        if not form.validate():
            return {
                    'successful': False,
                    'email': email
                    }

        user_object = self.bucket.get(str(email))
        user = user_object.get_data()

        if not user:
            return {
                    'successful': False,
                    'email': email
                    }

        if 'registration_complete' not in user:
            return {
                    'successful': False,
                    'email': email
                    }

        if user['password'] == str(password):
            return {
                    'successful': True,
                    'email': email
                    }
        else:
            return {
                    'successful': False,
                    'email': email
                    }

    def activate(self, email, confirmation_key):
        user_object = self.bucket.get(str(email))
        user = user_object.get_data()

        if user and confirmation_key == user['confirmation_key']:
            user['registration_complete'] = True
            user_object.set_data(user)
            user_object.store()
            return {'successful': True}

        return {'successful': False}


