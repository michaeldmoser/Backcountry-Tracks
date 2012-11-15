import sys
import json

from pprint import pprint

from riak import RiakClient

client = RiakClient()
buckets = client.get_buckets()


for bucket_name in buckets:
    documents = list()
    bucket = client.bucket(bucket_name)
    keys = bucket.get_keys()
    
    for key in keys:
        document = dict()
        obj = bucket.get(str(key))
        link_objs = obj.get_links()

        links = list()
        for link_obj in link_objs:
            link = {
                    'key': link_obj.get_key(),
                    'bucket': link_obj.get_bucket(),
                    'tag': link_obj.get_tag()
                    }

        usermeta = obj.get_usermeta()
        body = obj.get_data()
        document = {
                'links': links,
                'usermeta': usermeta,
                'body': body
                }

        documents.append(document)

    open(bucket_name, "w").write(json.dumps(documents))
        

    


