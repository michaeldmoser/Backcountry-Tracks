from setuptools import setup

setup(
    name = 'SmokeSignal',
    version = '0.1',
    packages = ['smokesignal'],
    test_suite = 'smokesignal',
    install_requires = '''
        pika
    ''',
    entry_points = {
        'console_scripts': ['smokesignal = smokesignal.script:main']
        }
    )

