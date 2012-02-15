from pkg_resources import load_entry_point

class ServiceLookup(object):

    def __init__(self, services_list, env, remoting_client):
        self.services = dict()
        self.services_list = services_list
        self.env = env
        self.remoting_client = remoting_client
        

    def get(self, routing_key):
        '''Return the service configured for use with routing_key'''
        if not self.services.has_key(routing_key):
            key = self.services_list[routing_key]
            dist, name = key.split('/')
            config = self.env.config[key]

            entrypoint = load_entry_point(dist, 'tripplanner.endpoint', name)
            self.services[routing_key] = entrypoint(config, self.env, self.remoting_client)


        return self.services[routing_key]()
        



        
