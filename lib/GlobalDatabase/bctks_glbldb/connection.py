from .realm import Realm

class Connection(object):

    def __init__(self, riak):
        self.riak = riak

    def Realm(self, name):
        return Realm(self.riak, name)
