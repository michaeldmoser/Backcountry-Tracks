import uuid

class TripsEnvironment(object):
    def __init__(self, env):
        self.env = env
        self.tripsdb = self.env.riak.get_database('trips')


    def add(self, owner=None, name=None, description=None, start=None, end=None):
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
                'end': end
                }
        new_trip = self.tripsdb.new(trip_id, data=trip)
        new_trip.store()

        return trip_id

