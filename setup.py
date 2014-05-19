#!/usr/bin/python
from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
    requires = [x.strip() for x in f if x.strip()]


setup(
    name='swift-webmode',
    version='0.1',
    description='Web Content Tools for Swift',
    author='Clay Gerrard',
    packages=find_packages(),
    install_requires=requires,
    entry_points={
        'paste.filter_factory': [
            'webauth=swift_webmode.webauth:filter_factory',
            'webtemplates=swift_webmode.webtemplates:filter_factory',
        ],
    },
)
