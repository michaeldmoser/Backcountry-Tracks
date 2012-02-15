from setuptools import setup

setup(
    name = 'MessagingService',
    version = '0.1',
    packages = ['bctmessagingservices'],
    test_suite = 'bctmessagingservices',
    entry_points = {
        'tripplanner.service': ['messagingservice = bctmessagingservices:EntryPoint'],
        },
    )

