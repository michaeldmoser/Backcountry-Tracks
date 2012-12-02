import importlib
import os
from os import path

from unittest import TestSuite, TestResult, TestLoader, TextTestRunner


def is_testable(root, sub_dir):
    init_file_path = path.join(root, sub_dir, '__init__.py')
    test_directory_path = path.join(root, sub_dir, 'tests', 'medium')

    if '.egg-info' in sub_dir:
        return False

    if not path.exists(init_file_path):
        return False

    if not path.isfile(init_file_path):
        return False

    if not path.exists(test_directory_path):
        return False

    if not path.isdir(test_directory_path):
        return False

    return True

def remove_ignored_directories(dirs):
    if 'testing' in dirs:
        dirs.remove('testing')
    if 'config' in dirs:
        dirs.remove('config')
    if '.git' in dirs:
        dirs.remove('.git')
    if 'tools' in dirs:
        dirs.remove('tools')

def discover(test_suite):
    loader = TestLoader()
    for root, dirs, files in os.walk('.'):
        remove_ignored_directories(dirs)
        if 'setup.py' not in files:
            continue

        sub_dirs = []
        for sub_dir in dirs:
            if not is_testable(root, sub_dir):
                continue

            package_path = path.join(root, sub_dir)
            top_level_dir = path.dirname(package_path)
            package_tests = loader.discover(package_path, top_level_dir=top_level_dir)
            test_suite.addTests(package_tests)

if __name__ == '__main__':
    test_suite = TestSuite()
    discover(test_suite)
    TextTestRunner(verbosity=0).run(test_suite)





