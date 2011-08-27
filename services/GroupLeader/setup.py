from setuptools import setup

setup(
    name = 'GroupLeader',
    version = '0.1',
    packages = ['groupleader'],
    test_suite = 'groupleader',
    install_requires = '''
        pika
    ''',
    entry_points = {
        'console_scripts': ['groupleader = groupleader.script:main']
        }
    )

