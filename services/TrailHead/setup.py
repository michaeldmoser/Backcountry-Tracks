from setuptools import setup

setup(
    name = 'TrailHead',
    version = '0.1',
    packages = ['trailhead'],
    test_suite = 'trailhead',
    install_requires = '''
        tornado >= 2.2
        pika
        python-daemon
        lockfile
    ''',
    entry_points = {
        'tripplanner.service': ['trailhead = trailhead:EntryPoint'],
        'tripplanner.web.files': ['trailhead = trailhead:Webroot'],
        },
    package_data = {
        '': ['webroot/*'],
        }
    )

