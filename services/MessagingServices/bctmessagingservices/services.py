from pkg_resources import load_entry_point
import logging

class ServiceLookup(object):

    def __init__(self, services_list, env, remoting_client):
        self.services = dict()
        self.services_list = services_list
        self.env = env
        self.remoting_client = remoting_client
        

    def get(self, routing_key):
        '''Return the service configured for use with routing_key'''
        if not self.services.has_key(routing_key):
            try:
                key = self.services_list[routing_key]
            except KeyError:
                logging.debug("List of services is: %s" % self.services_list)
                raise
            dist, name = key.split('/')
            config = self.env.config[key]

            entrypoint = load_entry_point(dist, 'tripplanner.endpoint', name)
            self.services[routing_key] = entrypoint(config, self.env, self.remoting_client)


        return self.services[routing_key]()
        



        
