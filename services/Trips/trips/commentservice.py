import uuid

class TripCommentService(object):

    def __init__(self, riak, trips_bucket, comments_bucket):
        self.riak = riak
        self.trips = self.riak.bucket(trips_bucket)
        self.comments = self.riak.bucket(comments_bucket)

    def list(self, trip_id):
        map_js_function = '''
            function (v) 
            {
                var data = JSON.parse(v.values[0].data);
                return [data];
            }
            '''

        trip_doc = self.trips.get(trip_id)

        def filter_comments(item):
            return item.get_tag() == 'comment'

        def extract_keys(item):
            return item.get_key()

        comment_links = filter(filter_comments, trip_doc.get_links())
        comment_keys = map(extract_keys, comment_links)
        
        mr = self.riak.map(map_js_function)
        for key in comment_keys:
            mr.add(self.comments.get_name(), key)

        result = mr.run()

        return result

    def add(self, trip_id, comment):
        trip_doc = self.trips.get(trip_id)
        
        comment_id = str(uuid.uuid4())
        comment_doc = self.comments.new(comment_id, comment)
        comment_doc.store()

        trip_doc.add_link(comment_doc, tag='comment')
        trip_doc.store()
