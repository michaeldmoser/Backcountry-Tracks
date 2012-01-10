import uuid
import time

class TripsEnvironment(object):
    def __init__(self, env):
        self.env = env
        self.tripsdb = self.env.riak.get_database('trips')

    def add_trips_to_user(self, user, trips):
        stored_trips = []
        for trip in trips:
            stored_trip = trip.copy()
            trip_id = self.add(owner = user.email, **trip)
            stored_trip.update({
                'id': trip_id,
                'owner': user.email
                });
            stored_trips.append(stored_trip)

        return stored_trips

    def add(self, owner=None, name=None, description=None, start=None, end=None, destination=None):
        """
        Add a new trips to the user's trip list
        """
        assert owner is not None, "You must provide a owner"
        assert name is not None, "You must provide a name for the trip"
        assert description is not None, "You must provide a description for the trip"
        assert start is not None, "You must provide a start for the trip"
        assert end is not None, "You must provide a end for the trip"

        trip_id = str(uuid.uuid4())
        trip = {
                'name': name,
                'description': description,
                'owner': owner,
                'id': trip_id,
                'start': start,
                'end': end,
                'destination': destination,
                }
        new_trip = self.tripsdb.new(trip_id, data=trip)
        new_trip.store()

        return trip_id

    def remove_all(self):
        '''
        Remove all trips that exist in the datbase
        '''
        keys = self.tripsdb.get_keys()
        for key in keys:
            trip = self.tripsdb.get(str(key))
            trip.delete()

        for x in range(50):
            keys = self.tripsdb.get_keys()
            if len(keys) == 0:
                return

            time.sleep(.1)

        assert False, "Database did not clear out in the alloted time"

    def get_by_name(self, name):
        '''
        Get a trip by it's name
        '''
        trip = None 

        keys = self.tripsdb.get_keys()
        for key in keys:
            trip_obj = self.tripsdb.get(str(key))
            trip_data = trip_obj.get_data()

            if trip_data['name'] == name:
                trip = trip_data
                trip['id'] = key
                break

        return trip

    def add_invitee(self, trip_id, person, status):
        '''
        Add the person to the trip with id trip_id

        person should be a user object
        '''
        trip = self.tripsdb.get(str(trip_id))

        trip_data = trip.get_data()
        if not trip_data.has_key('friends'):
            trip_data['friends'] = list()

        trip_data['friends'].append({
            'id': person.email,
            'first': person.first_name,
            'last': person.last_name,
            'email': person.email,
            'invite_status': status
            })

        trip.set_data(trip_data)
        trip.store()

    def get(self, trip_id):
        '''Get a trip by it's id'''
        trip_obj = self.tripsdb.get(str(trip_id))
        trip_data = trip_obj.get_data()

        return trip_data

    def add_trip_gear(self, user, trip_id, gear_list):
        '''
        Add gear in gear_list to trip_id for user
        '''
        trip = self.tripsdb.get(str(trip_id))

        trip_data = trip.get_data()
        
        if not trip_data.has_key('gear'):
            trip_data['gear'] = dict()

        trip_data['gear'].update({user.email: gear_list})

        trip.set_data(trip_data)
        trip.store()

    def add_group_gear(self, trip_id, gear_list):
        '''
        Add shared/group gear to trip_id
        '''
        trip = self.tripsdb.get(str(trip_id))

        trip_data = trip.get_data()
        
        if not trip_data.has_key('groupgear'):
            trip_data['groupgear'] = list()

        trip_data['groupgear'].extend(gear_list)

        trip.set_data(trip_data)
        trip.store()

        

        

