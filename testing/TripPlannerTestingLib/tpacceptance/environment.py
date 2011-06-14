from tptesting import environment

class Environment(object):
    def __init__(self):
        self.tpenviron = environment.create()

    def start_the_infrastructure(self):
        self.tpenviron.make_pristine()
        self.tpenviron.bringup_infrastructure()

    def add_user_to_application(self, user):
        app_user = getattr(self.tpenviron, user)
        self.tpenviron.create_user(app_user)



