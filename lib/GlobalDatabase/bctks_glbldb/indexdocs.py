
class IndexDoc(list):

    def __init__(self, document_id, riak, bucket_name):
        self.document_id = document_id
        self.riak = riak
        self.bucket = self.riak.bucket(bucket_name)

        self.riak_object = self.bucket.get(self.document_id) 
        if self.riak_object.exists() == False:
            self.riak_object = self.bucket.new(self.document_id)
            list_data = []
        else:
            list_data = self.riak_object.get_data()['documents']

        list.__init__(self, list_data)

    def store(self):
        document = { 'documents': list(self) }
        self.riak_object.set_data(document)
        self.riak_object.store()



