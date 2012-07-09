import uuid
import hashlib
import logging
log = logging.getLogger('Adventurer/service')

from bctservices.crud import BasicCRUDService
from .forms import LoginForm, RegisterForm
from .users import Users

class AdventurerRepository(BasicCRUDService):

    def __init__(self,
            bucket_name = 'adventurers',
            mailer = None,
            db = None,
            trailhead_url = 'http://www.backcountrytracks.com/',
            remoting = None
            ):
        self.riak = db
        self.bucket_name = bucket_name
        self.bucket = self.riak.bucket(bucket_name)
        self.trailhead_url = trailhead_url
        self.mailer = mailer
        self.remoting = remoting

        self.users = Users(self.bucket)

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
        clean_data['password'] = hashlib.sha256(clean_data['password']).hexdigest()
        del clean_data['password_again']

        #check that the user isn't already in the system
        try:
            user = self.users.get_by_email(email)
        except KeyError:
            pass
        else:
            log.debug('Duplicate registration for %s' % user['email'])
            result = {'successful': False, 'messages': {
                'form': ['This email address has already been registered.']
                }}
            return result

        new_registration = self.users.save(clean_data)

        self.send_complete_registration_email(
                email,
                clean_data['first_name'],
                clean_data['last_name'],
                confirmation_key
                )

        logging.debug("Newsletter subscribe field is: %s", data.get('subscribe'))
        if data.get('subscribe'):
            newsletter = self.remoting.service('Newsletter')
            command = newsletter.subscribe(data)
            self.remoting.call(command)

        log.debug('Completed registration for %s' % email)
        result = {'successful': True}
        return result

    def generate_confirmation_key(self):
        return str(uuid.uuid4())

    def get(self, email):
        user = self.users.get_by_email(email)
        del user['password']
        return user

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
            "Once you have completed your registration you can login to your BackcountryTracks.com account using your email address!" % (first_name, last_name)

        href = u'%s#activate/%s/%s' % (self.trailhead_url, email, confirmation_key)
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

        try:
            user = self.users.get_by_email(email)
        except KeyError:
            user = None
            logging.warn('No user found for %s', email)

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

        password_hashed = hashlib.sha256(password).hexdigest()
        if user['password'] == password_hashed:
            return {
                    'successful': True,
                    'email': email,
                    'key': user['key'],
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

    def __send_password_reset(self, user):
        template_vars = user.copy()
        template_vars['url'] = self.trailhead_url
        template_vars['reset_key'] = user['password_reset_key']

        message = """
        %(first_name)s %(last_name)s,

        So finish reseting your password please go to %(url)s/password/%(reset_key)s
        """ % template_vars

        to = [user['email']]

        email_service = self.remoting.service('Email')
        command = email_service.send(to=to,
                subject="Password reset for Backcountry Tracks",
                message=message)
        self.remoting.call(command)

    def reset_password(self, email):
        user_object = self.bucket.get(str(email))

        if not user_object.exists():
            raise Exception('The email does not exist')

        user = user_object.get_data()

        user['password_reset_key'] = str(uuid.uuid4())
        user_object.set_data(user)
        user_object.store()

        self.__send_password_reset(user)

        return True

    def validate_reset_key(self, key):
        mapred_js = """
            function (value, keyData, arg) {
                if (value.values[0].data.length < 1)
                    return [];

                var data = Riak.mapValuesJson(value)[0];
                if (data.password_reset_key == arg['reset_key'])
                    return [data];
                else
                    return [];
            }
        """

        mapreduce = self.riak.add(self.bucket_name)
        mapreduce.map(mapred_js, options={'arg': {'reset_key': key}})
        results = mapreduce.run()
        return bool(results) 

    def reset_change_password(self, reset_key, email, password):
        user_object = self.bucket.get(str(email))

        if not user_object.exists():
            raise Exception('The email does not exist')

        user = user_object.get_data()

        if user['password_reset_key'] != reset_key:
            raise Exception('The reset key is invalid.');

        user['password'] = hashlib.sha256(password).hexdigest()
        user['password_reset_key'] = None;
        user_object.set_data(user);
        user_object.store()

        return True




