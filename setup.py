#!/usr/bin/env python
# vim: set sw=4 et:

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import glob

__version__ = '0.1.0-dev0'


setup(
    name='crawlmanager',
    version=__version__,
    author='John Berlin',
    author_email='john.berlin@rhizome.org',
    license='Apache 2.0',
    packages=find_packages(exclude=['test']),
    url='https://github.com/webrecorder/crawlmanager',
    description='Webrecorder Experimental System',
    long_description=open('README.md').read(),
    provides=[
        'crawlmanager',
        ],
    install_requires=[
        'aiodns',
        'aiofiles',
        'aiohttp',
        'better_exceptions',
        'fastapi',
        'aioredis',
        'pyyaml',
        'uvloop',
        'ujson',
        ],
    zip_safe=True,
    entry_points="""
    """,
    test_suite='',
    tests_require=[
        'pytest',
        'mock',
        'requests',
        'fakeredis',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ]
)
