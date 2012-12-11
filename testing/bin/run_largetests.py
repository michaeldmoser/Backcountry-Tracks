from tptesting.runtests import TestSuite, discover, TextTestRunner

if __name__ == '__main__':
    test_suite = TestSuite()
    discover(test_suite, 'large')
    TextTestRunner(verbosity=0).run(test_suite)

