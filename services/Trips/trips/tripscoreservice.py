import uuid

class TripsCoreService(object):

    def __init__(self, riak, bucket_name):
        self.riak = riak
        self.bucket = self.riak.bucket(bucket_name)


    def _get_user_trip_index(self, user):
        index_doc = self.bucket.get(str(user))

        if index_doc.exists() is None:
            index = dict()
            index['documents'] = list()

            return index

        return index_doc.get_data()

    def create(self, owner, trip):
        index = self._get_user_trip_index(owner)

        trip_id = str(uuid.uuid4())
        trip['id'] = trip_id

        trip_doc = self.bucket.new(trip_id, trip)
        trip_doc.store()

        return trip


    def update(self, owner, obj_id, obj):
        catalog = self.catalog(owner)
        catalog.get(obj_id)


    def delete(self, owner, obj_id):
        catalog = self.catalog(owner)
        catalog.delete(obj_id)

    def list(self, owner):
        catalog = self.catalog(owner)
        items = catalog.list_items()
        return items

    def get(self, obj_id):
        return None


