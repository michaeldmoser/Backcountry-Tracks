from robot.libraries.BuiltIn import BuiltIn

from tptesting import environment

class Trips(object):
    def __init__(self):
        self.env = environment.create()
        self.trips = self.env.trips
        self.builtin = BuiltIn()

    def add_a_trip_invitee(self, person, trip_name, status='invited'):
        '''
        Make person and invitee on a trip
        '''
        adventurer = self.env.adventurer.get_by_name(person)
        trip = self.trips.get_by_name(trip_name)
        print '''DEBUG adventurer is %s''' % str(adventurer)
        print '''DEBUG trip name is %s''' % str(trip_name)
        self.env.trips.add_invitee(trip['id'], adventurer, status)

    def get_trip_by_name(self, trip_name):
        '''
        Get a trip from the database based on the name
        '''
        return self.trips.get_by_name(trip_name)


        





