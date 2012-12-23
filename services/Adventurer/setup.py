from setuptools import setup

setup(
    name = 'Adventurer',
    version = '0.2',
    packages = ['adventurer'],
    test_suite = 'adventurer',
    install_requires = '''
	wtforms
    ''',
    entry_points = {
        'tripplanner.endpoint': [
            'adventurer = adventurer:EntryPoint',
            ],
        'tripplanner.trailhead.handler': [
            'register = adventurer.register:registerhandler_factory',
            'activate = adventurer.register:registerhandler_factory',
            'user = adventurer.user:userhandler_factory',
            'login = adventurer.login:loginhandler_factory',
            'logout = adventurer.login:logouthandler_factory',
            'passreset = adventurer.passwordreset:passwordreset_factory'
            ],
        }
    )

