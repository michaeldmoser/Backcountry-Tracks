import uuid

class UserGear(object):
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
        self.gear_bucket_name = bucket_name

    def list(self, owner):
        '''
        Return a list of all pieces of gear owned by @owner
        '''
        mapreduce = self.riak.add(self.gear_bucket_name)
        mapreduce.map(self.list_mapreduce, options={'arg': {'owner': owner}})
        return mapreduce.run()

    def create(self, owner, pieceofgear):
        '''
        Add a new piece of gear to an adventurer's gear list
        '''
        bucket = self.riak.bucket(self.gear_bucket_name)

        key = str(uuid.uuid4())
        gear_data = pieceofgear.copy()
        gear_data['id'] = key
        gear_data['owner'] = owner

        riak_object = bucket.new(key, data=gear_data)
        riak_object.store()

        return gear_data

    def update(self, owner, gear_id, pieceofgear):
        '''
        Update a piece of gear in the adventurer's gear list
        '''
        bucket = self.riak.bucket(self.gear_bucket_name)

        gear_object = bucket.get(str(gear_id))
        gear_object.set_data(pieceofgear)
        gear_object.store()

        return gear_object.get_data()



        

    

