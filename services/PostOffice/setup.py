from setuptools import setup

setup(
    name = 'PostOffice',
    version = '0.1',
    packages = ['postoffice'],
    test_suite = 'postoffice',
    entry_points = {
        'tripplanner.endpoint': ['postoffice = postoffice:EntryPoint'],
        }
    )

