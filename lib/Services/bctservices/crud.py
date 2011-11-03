import uuid

class BasicCRUDService(object):
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


    def create(self, owner, obj):
        '''
        Add a new object
        '''
        bucket = self.riak.bucket(self.bucket_name)

        key = str(uuid.uuid4())
        data = obj.copy()
        data['id'] = key
        data['owner'] = owner

        riak_object = bucket.new(key, data=data)
        riak_object.store()

        return data

    def update(self, owner, obj_id, obj):
        '''
        Update a obj in the adventurer's list of objs
        '''
        bucket = self.riak.bucket(self.bucket_name)

        gear_object = bucket.get(str(obj_id))
        gear_object.set_data(obj)
        gear_object.store()

        return gear_object.get_data()

    def delete(self, owner, obj_id):
        '''
        Remove a obj from the adventurer's obj list
        '''
        bucket = self.riak.bucket(self.bucket_name)
        gear_object = bucket.get(str(obj_id))
        gear_object.delete()

    def list(self, owner):
        '''
        Return a list of all objs owned by @owner
        '''
        mapreduce = self.riak.add(self.bucket_name)
        mapreduce.map(self.list_mapreduce, options={'arg': {'owner': owner}})
        return mapreduce.run()

    def get(self, obj_id):
        bucket = self.riak.bucket(self.bucket_name)
        document_object = bucket.get(str(obj_id))
        return document_object.get_data()





