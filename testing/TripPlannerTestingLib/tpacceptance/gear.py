from robot.libraries.BuiltIn import BuiltIn

from tptesting import environment

class Gear(object):

    def __init__(self):
        self.env = environment.create()
        self.gear = self.env.gear
        self.builtin = BuiltIn()

    def create_a_basic_set_of_gear_for(self, user): 
       '''
       Populate the database with a list of gear owned by user
       '''
       gear_data = self.env.data['gear']

       for item in gear_data:
           new_gear = item.copy()
           new_gear['owner'] = user
           self.gear.add_item(**new_gear)

    def clear_the_gear_database(self):
        '''
        Removes all gear persent in the gear bucket
        '''
        self.gear.remove_all()


