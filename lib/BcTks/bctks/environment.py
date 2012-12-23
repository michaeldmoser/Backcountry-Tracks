from pkg_resources import load_entry_point

class BcTksEnvironment(object):
    def __init__(self, config):
        self.config = config

    def get_component(self, group, dist, name):
        return load_entry_point(dist, group, name)

    def get_component_factory(self, group, dist, name):
        entry_point = self.get_component(group, dist, name)
        return entry_point(self)


