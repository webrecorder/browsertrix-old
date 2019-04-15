#!/usr/bin/env python
# vim: set sw=4 et:

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import glob

__version__ = '0.1.0-dev0'

def load_requirements(filename):
    with open(filename, 'rt') as fh:
        requirements = fh.read().rstrip().split('\n')
    return requirements


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
    install_requires=load_requirements('requirements.txt'),
    zip_safe=True,
    entry_points="""
    """,
    test_suite='',
    tests_require=load_requirements('test-local-requirements.txt'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ]
)
