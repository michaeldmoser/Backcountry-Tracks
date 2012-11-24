import unittest

import uuid

from bctks_glbldb.connection import Connection
from tptesting.fakeriak import RiakClientFake
from tptesting import environment

class RiakFakeTestCase(unittest.TestCase):

    def setUp(self):
        self.environ = environment.create()
        self.riak = RiakClientFake()
        self.bucket = self.riak.bucket(self.BUCKET)
        self.dbcon = Connection(self.riak)
        self.realm = self.dbcon.Realm(self.BUCKET)

        self.adventurer = str(uuid.uuid4())

        try:
            self.continueSetup()
        except AttributeError:
            pass

