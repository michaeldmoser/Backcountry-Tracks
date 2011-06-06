import logging

class Application(object):
    def __init__(self, bucket=None):
        self.bucket = bucket

    def register(self, data):
        '''
        Registers a new adventurer with the system by saving it to the database
        '''
        new_registration = self.bucket.new(data['email'], data = data)
        new_registration.store()

