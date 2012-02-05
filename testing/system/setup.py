from setuptools import setup

setup(
    name = 'TripPlannerSystemTesting',
    version = '0.3',
    packages = ['tpsystest'],
    test_suite = 'tpsystest',
    install_requires = [
        'riak',
        'python-dateutil < 2.0',
        ],
    package_data = {
        '': ['*'],
        }
    )
        
