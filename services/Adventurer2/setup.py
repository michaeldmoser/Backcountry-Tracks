from setuptools import setup

setup(
    name = 'Adventurer2',
    version = '0.1',
    packages = ['adventurer2'],
    test_suite = 'adventurer2',
    entry_points = {
        'tripplanner.service': ['adventurer = adventurer2:EntryPoint'],
        'tripplanner.trailhead.handler': [
            'register = adventurer2.register:RegisterHandler',
            'activate = adventurer2.register:ActivateHandler',
            'user = adventurer2.user:UserHandler',
            'login = adventurer2.login:LoginHandler',
            ],
        }
    )

