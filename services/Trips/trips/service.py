import uuid

from bctservices.crud import BasicCRUDService

class TripsDb(BasicCRUDService):

    def invite(self, trip_id, invitor, invite):
        result = invite.copy()
        result['id'] = str(uuid.uuid4())

        bucket = self.riak.bucket(self.bucket_name)
        trip = bucket.get(str(trip_id))
        trip_data = trip.get_data()

        if not trip_data.has_key('friends'):
            trip_data['friends'] = []

        trip_data['friends'].append(result)
        trip.set_data(trip_data)
        trip.store()

        return result

