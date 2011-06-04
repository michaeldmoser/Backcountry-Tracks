from setuptools import setup

setup(
    name = 'Adventurer',
    version = '0.1',
    packages = ['adventurer'],
    test_suite = 'adventurer',
    install_requires = '''
        pika
        python-daemon
        lockfile
    ''',
    entry_points = {
        'console_scripts': ['adventurer = adventurer.script:main']
        }
    )

