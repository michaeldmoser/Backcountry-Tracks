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
        'tripplanner.service': ['trips = trips:EntryPoint'],
        'tripplanner.trailhead.handler': [
            'trips = trips.handlers:TripsHandler',
            'trip = trips.handlers:TripHandler',
            'friends = trips.friends:FriendsHandler',
            ],
        'tripplanner.web.files': ['trips = trips:Webroot'],
        },
    package_data = {
        '': ['webroot/*'],
        }
    )

