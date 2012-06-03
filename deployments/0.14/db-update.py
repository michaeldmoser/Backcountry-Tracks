import riak
import sys
from pprint import pprint
import uuid

if __name__ == '__main__':
    client = riak.RiakClient()

    trips_bucket = client.bucket('trips')

    keys = trips_bucket.get_keys()
    for trip_key in keys:
        obj = trips_bucket.get(str(trip_key))
        usermeta = obj.get_usermeta()
        if 'object_type' not in usermeta:
            mark_as_trip(obj)

        if usermeta['object_type'] != 'trip':
            continue

        links = obj.get_links()
        gear_links = filter(lambda x: x.get_tag() in ['gear_personal', 'gear_group'], links)

        for gear_link in gear_links:
            obj.remove_link(gear_link)
            gear = gear_link.get()
            data = gear.get_data()

            print "OLD GEAR ---------------------------------------"
            pprint(data)
            data['gear_id'] = data['id']
            data['id'] = str(uuid.uuid4())
            print "NEW GEAR ---------------------------------------"
            pprint(data)

            newgear = trips_bucket.new(data['id'], data)
            newgear.store()
            tag = gear_link.get_tag()
            obj.add_link(newgear, tag=tag)

        obj.store()


