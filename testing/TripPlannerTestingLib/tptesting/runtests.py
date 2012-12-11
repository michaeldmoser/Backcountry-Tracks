import importlib
import os
from os import path

from unittest import TestSuite, TestResult, TestLoader, TextTestRunner


def is_testable(root, sub_dir, test_type="small"):
    init_file_path = path.join(root, sub_dir, '__init__.py')
    test_directory_path = path.join(root, sub_dir, 'tests', test_type)
    test_directory_init_file = path.join(root, sub_dir, 'tests', test_type, '__init__.py')

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

def discover(test_suite, test_type="small"):
    loader = TestLoader()
    for root, dirs, files in os.walk('.'):
        remove_ignored_directories(dirs)
        if 'setup.py' not in files:
            continue

        sub_dirs = []
        for sub_dir in dirs:
            if not is_testable(root, sub_dir, test_type):
                continue

            package_path = path.join(root, sub_dir, 'tests', test_type)
            package_tests = loader.discover(package_path, top_level_dir=root)
            test_suite.addTests(package_tests)


