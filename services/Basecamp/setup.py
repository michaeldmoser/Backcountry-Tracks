from setuptools import setup

setup(
    name = 'Basecamp',
    version = '0.1',
    packages = ['basecamp'],
    test_suite = 'basecamp',
    install_requires = '''
        pika
    ''',
    entry_points = {
        'tripplanner.web.files': ['basecamp = basecamp:Webroot'],
        },
    package_data = {
        '': ['webroot/*'],
        }
    )

