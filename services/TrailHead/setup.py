from setuptools import setup

setup(
    name = 'TrailHead',
    version = '0.1',
    packages = ['trailhead'],
    test_suite = 'trailhead',
    install_requires = '''
        tornado
        pika
        grizzled-python
    ''',
    entry_points = {
        'console_scripts': ['trailhead = trailhead.script:main']
        }
    )

