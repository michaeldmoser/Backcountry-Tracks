import time
import sys

from tptesting import environment
import robot.libraries.BuiltIn
import logging

import mailbox

class Environment(object):
    def __init__(self):
        self.tpenviron = environment.create()

    def start_the_infrastructure(self):
        self.tpenviron.make_pristine()
        self.tpenviron.bringup_infrastructure()

    def add_user_to_application(self, user):
        app_user = getattr(self.tpenviron, user)
        self.tpenviron.create_user(app_user)

    def clear_the_mailbox(self):
        self.tpenviron.clear_mbox()

    def add_gear_item(self, name, description, weight):
        """
        Create a gear item for the currently active user
        """
        builtin = robot.libraries.BuiltIn.BuiltIn()
        variables = builtin.get_variables()
        current_user = variables['${CURRENT_USER}']
        
        self.tpenviron.gear.add_item(current_user['email'], name, description, weight)

    def clear_the_gear_list(self):
        '''Removes all gear in the database'''
        self.tpenviron.gear.remove_all()

    def create_basic_trip_list(self):
        '''
        Prepopulate the database with a list of trips
        '''
        builtin = robot.libraries.BuiltIn.BuiltIn()
        variables = builtin.get_variables()
        current_user = variables['${CURRENT_USER}']

        trips = self.tpenviron.data['trips']

        self.tpenviron.trips.remove_all()
        for trip in trips:
            self.tpenviron.trips.add(owner=current_user.email, **trip)

    def create_a_basic_trip_list_for_user(self, user):
        '''
        Populate the database with a list of trips for the specified user
        '''
        trips = self.tpenviron.data['trips']

        self.tpenviron.trips.remove_all()
        for trip in trips:
            self.tpenviron.trips.add(owner=user, **trip)

    def get_person_by_name(self, first_name):
        '''
        Get the user object for the person identified by their first name
        '''
        person = getattr(self.tpenviron, first_name.lower())
        return person


    def get_email_for(self, email_address):
        '''
        Retrieves the first email from the configured email box addressed to ${email_address}
        '''
        mbox_path = self.tpenviron.get_config_for('mbox_file')

        for tries in range(30):
            mbox = mailbox.mbox(mbox_path)
            for message in mbox.values():
                if email_address in message.get('To'):
                    return message.get_payload(decode=True)

            time.sleep(.1)


