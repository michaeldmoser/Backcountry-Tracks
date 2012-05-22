import riak
import sys
from pprint import pprint

def mark_as_trip(obj):
    usermeta = obj.get_usermeta()
    usermeta['object_type'] = 'trip'
    obj.set_usermeta(usermeta)

def move_personal_gear(obj):
    data = obj.get_data()

    gear_list = list()
    for user, gear in data.get('gear', {}).items():
        gear_list.extend(gear) 

    for gear in gear_list:
        gear_obj = trips_bucket.new(str(gear['id']), gear)
        gear_obj.store()
        obj.add_link(gear_obj, tag="gear_personal")

    try:
        del data['gear']
    except KeyError:
        return

    obj.set_data(data)

def move_group_gear(obj):
    data = obj.get_data()

    gear_list = data.get('groupgear', [])
    for gear in gear_list:
        gear_obj = trips_bucket.new(str(gear['id']), gear)
        gear_obj.store()
        obj.add_link(gear_obj, tag="gear_group")

    try:
        del data['groupgear']
    except KeyError:
        return

    obj.set_data(data)


if __name__ == '__main__':
    client = riak.RiakClient()

    trips_bucket = client.bucket('trips')

    keys = trips_bucket.get_keys()
    for trip_key in keys:
        obj = trips_bucket.get(str(trip_key))
        usermeta = obj.get_usermeta()
        if 'object_type' not in usermeta:
            mark_as_trip(obj)

        if usermeta['object_type'] in ['comment', 'gear', 'route']:
            continue

        move_personal_gear(obj)
        move_group_gear(obj)

        obj.store()


