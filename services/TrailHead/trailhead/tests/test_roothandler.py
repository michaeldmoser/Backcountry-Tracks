import unittest

from tornado.web import RequestHandler
from trailhead.server import RootHandler

class TestRootHandler(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_has_get_method(self):
        """RootHandler should be able to respond to HTTP GETs"""
        assert(hasattr(RootHandler, 'get'))

    def test_inherits_from_requesthandler(self):
        """Tornado requires inheriting from RequestHandler"""
        assert(issubclass(RootHandler, RequestHandler))

if __name__ == '__main__':
    unittest.main()
    
