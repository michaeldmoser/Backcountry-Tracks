
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
        mapreduce.map(self.list_mapreduce, {'owner': owner})
        return mapreduce.run()

    

