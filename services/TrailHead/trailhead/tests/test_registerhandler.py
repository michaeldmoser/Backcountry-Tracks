import unittest

from tornado.web import RequestHandler
from trailhead.register import RegisterHandler

class TestRegisterHandler(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_implements_post_method(self):
        """RegisterHandler should be able to respond to HTTP POSTs, in other words it must implement the post() method"""
        self.assertNotEquals(RegisterHandler.post, RequestHandler.post)

    def test_inherits_from_requesthandler(self):
        """Tornado requires inheriting from RequestHandler"""
        assert(issubclass(RegisterHandler, RequestHandler))

if __name__ == '__main__':
    unittest.main()

