import urllib2
import cookielib
import json

class UserTemplate(dict):
    '''
    UserTemplate instances store information about standard users used
    in testing the system.

    === properties ===
      first_name:: User's first name
      last_name:: User's last name
      email:: User's email address
      birthdate:: Birth date as YYYY-MM-DD
      password:: The password for this user

    '''
    def set_trailhead_url(self, url):
        self.trailhead_url = url

    def __get_first_name(self):
        return self['first_name']
    first_name = property(fget=__get_first_name)

    def __get_last_name(self):
        return self['last_name']
    last_name = property(fget=__get_last_name)

    def __get_email(self):
        return self['email']
    email = property(fget=__get_email)

    def __get_birthdate(self):
        return self['birthdate']
    birthdate = property(fget=__get_birthdate)

    def __get_password(self):
        return self['password']
    password = property(fget=__get_password)

    def login(self):
        jar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))

        login_url = self.trailhead_url + '/login'
        credentials = {
                'email': self['email'],
                'password': self['password']
                }

        login_request = urllib2.Request(
                login_url,
                json.dumps(credentials),
                headers = {'Content-Type': 'application/json'}
                )
        response = opener.open(login_request)
        response.read()

        return opener


