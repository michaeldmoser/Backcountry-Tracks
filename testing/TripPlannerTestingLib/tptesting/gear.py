import uuid

class Gear(object):
    def __init__(self, environment):
        self.environ = environment
        self.geardb = self.environ.riak.get_database('personal_gear')


    def add_item(self, owner=None, name=None, description=None, weight=None):
        """
        Add a new piece of gear to the user's inventory
        """
        assert owner is not None, "You must provide a owner"
        assert name is not None, "You must provide a name for the gear"
        assert description is not None, "You must provide a description for the gear"
        assert weight is not None, "You must provide a weight for the gear"

        gear_id = str(uuid.uuid4())
        gear_item = {
                'name': name,
                'description': description,
                'weight': weight,
                'owner': owner,
                'id': gear_id,
                }
        new_gear = self.geardb.new(gear_id, data=gear_item)
        new_gear.store()

        return gear_id

    def remove_all(self):
        '''Removes all gear found in the database'''
        keys = self.geardb.get_keys()
        for key in keys:
            gear = self.geardb.get(str(key))
            gear.delete()

    def add_gear_to_user(self, user, gear_list):
        '''
        Mass add a list of gear to user
        '''
        stored_gear = []

        for gear in gear_list:
            gear_item = gear.copy()
            gear_id = self.add_item(owner=user.email, **gear_item)

            gear_item.update({
                'id': gear_id,
                'owner': user.email
                })

            stored_gear.append(gear_item)

        return stored_gear





