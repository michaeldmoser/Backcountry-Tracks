from setuptools import setup

setup(
    name = 'Adventurer',
    version = '0.2',
    packages = ['adventurer'],
    test_suite = 'adventurer',
    entry_points = {
        'tripplanner.endpoint': [
            'adventurer = adventurer:EntryPoint',
            'users = adventurer:UsersEntryPoint',
            ],
        'tripplanner.trailhead.handler': [
            'register = adventurer.register:RegisterHandler',
            'activate = adventurer.register:ActivateHandler',
            'user = adventurer.user:UserHandler',
            'login = adventurer.login:LoginHandler',
            'logout = adventurer.login:LogoutHandler',
            'passreset = adventurer.passwordreset:PasswordResetHandler',
            ],
        }
    )

