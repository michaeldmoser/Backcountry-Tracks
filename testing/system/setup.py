from setuptools import setup

setup(
    name = 'TripPlannerSystemTesting',
    version = '0.1',
    packages = ['tpsystest'],
    test_suite = 'tpsystest',
    install_requires = [
        'riak'
        ],
    package_data = {
        '': ['*'],
        }
    )
        
