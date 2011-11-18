import subprocess
from os import path
import os

class AdventurerEnvironment(object):
    def __init__(self, environment):
        self.environment = environment
        self.config = self.environment.get_config_for('adventurer')

    def create_user(self, name):
        '''Creates a known user in the adventurer database'''
        riak = self.environment.riak.get_database('adventurers')

        user_to_create = getattr(self.environment, name.lower())
        user = riak.new(user_to_create.email, user_to_create)
        user.store()



