
class UserTemplate(object):
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

    def __init__(self, user):
        '''
        user:: is a dict() with keys matching the properties
        '''
        self.__user = user

    def __get_first_name(self):
        return self.__user['first_name']
    first_name = property(fget=__get_first_name)

    def __get_last_name(self):
        return self.__user['last_name']
    last_name = property(fget=__get_last_name)

    def __get_email(self):
        return self.__user['email']
    email = property(fget=__get_email)

    def __get_birthdate(self):
        return self.__user['birthdate']
    birthdate = property(fget=__get_birthdate)

    def __get_password(self):
        return self.__user['password']
    password = property(fget=__get_password)
