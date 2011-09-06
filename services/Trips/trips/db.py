import uuid

class TripsDb(object):
    list_mapreduce = """
        function (value, keyData, arg) {
            var data = Riak.mapValuesJson(value)[0];
            if (data.owner == arg['owner'])
                return [data];
            else
                return [];
        }
    """
    def __init__(self, riak, bucket_name):
        self.riak = riak
        self.bucket_name = bucket_name


    def create(self, owner, trip):
        '''
        Add a new trip to an adventurer's trip list
        '''
        bucket = self.riak.bucket(self.bucket_name)

        key = str(uuid.uuid4())
        data = trip.copy()
        data['id'] = key
        data['owner'] = owner

        riak_object = bucket.new(key, data=data)
        riak_object.store()

        return data

    def update(self, owner, trip_id, trip):
        '''
        Update a trip in the adventurer's list of trips
        '''
        bucket = self.riak.bucket(self.bucket_name)

        gear_object = bucket.get(str(trip_id))
        gear_object.set_data(trip)
        gear_object.store()

        return gear_object.get_data()

    def delete(self, owner, trip_id):
        '''
        Remove a trip from the adventurer's trip list
        '''
        bucket = self.riak.bucket(self.bucket_name)
        gear_object = bucket.get(str(trip_id))
        gear_object.delete()

    def list(self, owner):
        '''
        Return a list of all trips owned by @owner
        '''
        mapreduce = self.riak.add(self.bucket_name)
        mapreduce.map(self.list_mapreduce, options={'arg': {'owner': owner}})
        return mapreduce.run()




