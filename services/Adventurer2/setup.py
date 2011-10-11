from setuptools import setup

setup(
    name = 'Adventurer2',
    version = '0.1',
    packages = ['adventurer2'],
    test_suite = 'adventurer2',
    entry_points = {
        'tripplanner.service': ['adventurer = adventurer2:EntryPoint']
        }
    )

