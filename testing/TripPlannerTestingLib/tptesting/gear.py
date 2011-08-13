import uuid

class Gear(object):
    def __init__(self, environment):
        self.environ = environment
        self.geardb = self.environ.riak.get_database('personal_gear')


    def add_item(self, user, name, description, weight):
        """
        Add a new piece of gear to the user's inventory
        """
        gear_id = str(uuid.uuid4())
        gear_item = {
                'name': name,
                'description': description,
                'weight': weight,
                'user': user,
                }
        new_gear = self.geardb.new(gear_id, data=gear_item)
        new_gear.store()

        return gear_id

