
class AdventurerRepository(object):

    def __init__(self, riak, bucket_name):
        self.riak = riak
        self.bucket_name = bucket_name
        self.bucket = self.riak.bucket(self.bucket_name)

    def get(self, user_email):
        document_object = self.bucket.get(user_email)
        return document_object.get_data()


