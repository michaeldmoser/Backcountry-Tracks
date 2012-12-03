import uuid

class TripsCoreService(object):

    def __init__(self, riak, bucket_name):
        self.riak = riak
        self.bucket = self.riak.bucket(bucket_name)


    def _get_trip_index(self, owner):
        index_doc = self.bucket.get(str(owner))

        if not index_doc.exists():
            index = dict()
            index['documents'] = list()

            return index

        return index_doc.get_data()

    def _update_trip_index(self, owner, trip_id):
        index = self._get_trip_index(owner)

        if trip_id in index['documents']:
            return

        index['documents'].append(trip_id)

        index_doc = self.bucket.new(owner, index)
        index_doc.store()

    def create(self, owner, trip):
        trip_id = str(uuid.uuid4())
        trip['id'] = trip_id
        trip['owner'] = owner

        trip_doc = self.bucket.new(trip_id, trip)
        trip_doc.store()

        self._update_trip_index(owner, trip_id)

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


