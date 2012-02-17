from setuptools import setup

setup(
    name = 'Gear',
    version = '0.1',
    packages = ['gear'],
    test_suite = 'gear',
    install_requires = '''
        pika
    ''',
    entry_points = {
        'tripplanner.endpoint': ['gear = gear:GearEntryPoint'],
        'tripplanner.trailhead.handler': ['gear = gear.handlers:UserGearListHandler'],
        'tripplanner.web.files': ['gear = gear:Webroot'],
        },
    package_data = {
        '': ['webroot/*'],
        }
    )

