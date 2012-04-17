from setuptools import setup

setup(
    name = 'BctksNewsletter',
    version = '0.1',
    packages = ['bctksnewsletter'],
    test_suite = 'bctksnewsletter',
    install_requires =  '''
        MailSnake
        ''',
    entry_points = {
        'tripplanner.endpoint': ['newsletter = bctksnewsletter:EntryPoint'],
        }
    )

