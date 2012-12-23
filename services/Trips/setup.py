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
        'tripplanner.endpoint': [
            'trips = trips:EntryPoint',
            'trips.core = trips:TripsCoreEntry',
            'trips.comments = trips:TripsCommentsEntry',
            ],
        'tripplanner.trailhead.handler': [
            'trips = trips.handlers:create_tripshandler',
            'trip = trips.handlers:create_triphandler',
            'friends = trips.friends:create_friendshandler',
            'gear = trips.gear_handler:create_gearhandler',
            'groupgear = trips.group_gear_handler:create_groupgearhandler',
            'route = trips.route_handler:create_routehandler',
            'comments = trips.comments_handler:create_commentshandler',
            ],
        'tripplanner.web.files': ['trips = trips:Webroot'],
        },
    package_data = {
        '': ['webroot/*'],
        }
    )

