import unittest

from trailhead import script

        

class TestMain(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_cli_main(self):
        """script.main() should exist"""
        assert(hasattr(script, "main"))

        

if __name__ == '__main__':
    unittest.main()
