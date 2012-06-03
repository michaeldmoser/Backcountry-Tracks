import riak
import sys
from pprint import pprint
import uuid

if __name__ == '__main__':
    client = riak.RiakClient()

    trips_bucket = client.bucket('trips')
    adventurer_bucket = client.bucket('adventurers')

    keys = trips_bucket.get_keys()
    for trip_key in keys:
        obj = trips_bucket.get(str(trip_key))
        usermeta = obj.get_usermeta()
        print obj.get_data()

        try:
            if usermeta['object_type'] != 'trip':
                continue
        except KeyError:
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

            tag = gear_link.get_tag()

            newgear = trips_bucket.new(data['id'], data)
            newgear.set_usermeta({'object_type': tag})
            newgear.store()

            obj.add_link(newgear, tag=tag)

        tripdata = obj.get_data()
        owner = adventurer_bucket.get(str(tripdata['owner']))
        ownerdata = owner.get_data()
        tripdata['friends'].append({
            'invite_status': 'owner',
            'first': ownerdata['first_name'],
            'last': ownerdata['last_name'],
            'email': ownerdata['email'],
            'id': ownerdata['email'],
            })


        obj.store()


