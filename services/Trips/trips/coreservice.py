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

    def _remove_trip_from_index(self, owner, trip_id):
        index = self._get_trip_index(owner)

        try:
            index['documents'].remove(trip_id)
        except ValueError:
            return

        index_doc = self.bucket.new(owner, index)
        index_doc.store()

    def _get_list(self, keys):
        map_js_function = '''
            function (v) 
            {
                var data = JSON.parse(v.values[0].data);
                data.id = v.key;
                return [data];
            }
            '''
        mr = self.riak.map(map_js_function)
        
        for key in keys:
            mr.add(self.bucket.get_name(), key)

        results = mr.run()
        return results

    def create(self, owner, trip):
        trip_id = str(uuid.uuid4())
        trip['id'] = trip_id
        trip['owner'] = owner

        trip_doc = self.bucket.new(trip_id, trip)
        trip_doc.store()

        self._update_trip_index(owner, trip_id)

        return trip

    def update(self, owner, trip_id, trip):
        trip['owner'] = owner

        trip_doc = self.bucket.get(trip_id)
        trip_doc.set_data(trip)
        trip_doc.store()

        return trip

    def delete(self, owner, trip_id):
        trip_doc = self.bucket.get(trip_id)
        self._remove_trip_from_index(owner, trip_id)
        trip_doc.delete()

    def list(self, owner):
        index = self._get_trip_index(owner)
        if len(index['documents']) < 1:
            return []

        return self._get_list(index['documents'])

    def get(self, obj_id):
        return None


