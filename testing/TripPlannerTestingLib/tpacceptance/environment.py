from tptesting import environment
import robot.libraries.BuiltIn

class Environment(object):
    def __init__(self):
        self.tpenviron = environment.create()

    def start_the_infrastructure(self):
        self.tpenviron.make_pristine()
        self.tpenviron.bringup_infrastructure()

    def add_user_to_application(self, user):
        app_user = getattr(self.tpenviron, user)
        self.tpenviron.create_user(app_user)

    def add_gear_item(self, name, description, weight):
        """
        Create a gear item for the currently active user
        """
        builtin = robot.libraries.BuiltIn.BuiltIn()
        variables = builtin.get_variables()
        current_user = variables['${CURRENT_USER}']
        
        self.tpenviron.gear.add_item(current_user['email'], name, description, weight)




