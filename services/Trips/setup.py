from setuptools import setup

setup(
    name = 'Trips',
    version = '0.1',
    packages = ['trips'],
    test_suite = 'trips',
    install_requires = '''
        pika
    ''',
    entry_points = {
        'tripplanner.service': ['trips = trips:EntryPoint']
        }
    )

