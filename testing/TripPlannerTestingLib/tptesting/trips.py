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

