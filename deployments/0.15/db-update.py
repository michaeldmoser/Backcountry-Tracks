import uuid

from riak import RiakClient, RiakPbcTransport

riak = RiakClient(port=8087, transport_class=RiakPbcTransport)


def convert_adventurers():
    bucket = riak.bucket('adventurers')
    keys = bucket.get_keys()

    for key in keys:
        obj = bucket.get(str(key))
        adventurer_data = obj.get_data()

        adventurer_id = str(uuid.uuid4())
        adventurer_obj = bucket.new(adventurer_id, data=adventurer_data)
        adventurer_obj.store()

        obj.set_data({'key': adventurer_id})
        obj.store()
        
    

def main():
    convert_adventurers()


if __name__ == "__main__":
    main()
