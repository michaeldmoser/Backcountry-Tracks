import sys

from pprint import pprint

from riak import RiakClient

if len(sys.argv) < 2:
    print "You need to provide a bucket name to dump"
    sys.exit(1)

client = RiakClient()
bucket = client.bucket(sys.argv[1])

if len(sys.argv) > 2:
    obj = bucket.get(str(sys.argv[2]))
    pprint(obj.get_data())
else:
    for key in bucket.get_keys():
        obj = bucket.get(str(key))
        print key
        pprint(obj.get_data())
        print
        print '---------------------------'
        print
