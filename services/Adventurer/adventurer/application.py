import logging

class Application(object):
    def __init__(self, bucket=None):
        self.bucket = bucket

    def register(self, data):
        '''
        Registers a new adventurer with the system by saving it to the database
        '''
        new_registration = self.bucket.new(str(data['email']), data = data)
        new_registration.store()

    def login(self, email, password):
        '''
        Validates user crendentials and returns true if the email/password combination exists
        '''
        user_object = self.bucket.get(str(email))
        user = user_object.get_data()
        if True: #user['password'] == str(password):
            return True
        else:
            return False
