from setuptools import setup

setup(
    name = 'BackcountryTracks_Messaging',
    version = '0.1',
    packages = ['bctmessaging'],
    test_suite = 'bctmessaging',
    entry_points = {
        'bctks.messaging': [
            'MessagingBuilder = bctmessaging.connection:messaging_builder_factory',
            ]
        },
    )

