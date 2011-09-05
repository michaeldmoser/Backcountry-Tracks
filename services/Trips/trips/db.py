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

    # FIXME: This is bad style but I know that I'll be copying this code soon
    #def list(self, owner):
    #    '''
    #    Return a list of all pieces of gear owned by @owner
    #    '''
    #    mapreduce = self.riak.add(self.gear_bucket_name)
    #    mapreduce.map(self.list_mapreduce, options={'arg': {'owner': owner}})
    #    return mapreduce.run()

    #def update(self, owner, gear_id, pieceofgear):
    #    '''
    #    Update a piece of gear in the adventurer's gear list
    #    '''
    #    bucket = self.riak.bucket(self.gear_bucket_name)

    #    gear_object = bucket.get(str(gear_id))
    #    gear_object.set_data(pieceofgear)
    #    gear_object.store()

    #    return gear_object.get_data()

    #def delete(self, owner, gear_id):
    #    '''
    #    Remove a piece of gear from the adventurer's gear list
    #    '''
    #    bucket = self.riak.bucket(self.gear_bucket_name)
    #    gear_object = bucket.get(str(gear_id))
    #    gear_object.delete()


