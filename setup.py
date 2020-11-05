#!/usr/bin/env python
# vim: set sw=4 et:

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import glob

__version__ = '0.1.0.dev0'

def load_requirements(filename):
    """
    Load requirements from a file.

    Args:
        filename: (str): write your description
    """
    with open(filename, 'rt') as fh:
        requirements = fh.read().rstrip().split('\n')
    return requirements


setup(
    name='browsertrix-cli',
    version=__version__,
    author='John Berlin, Ilya Kreymer',
    author_email='john.berlin@rhizome.org, ikreymer@gmail.com',
    license='Apache 2.0',
    #packages=find_packages(exclude=['test']),
    packages=['browsertrix_cli'],
    url='https://github.com/webrecorder/browsertrix',
    description='Browsertrix CLI: Commandline interface for Webrecorder crawling system',
    long_description=open('README.md').read(),
    provides=[
        'browsertrix_cli',
        ],
    install_requires=load_requirements('cli-requirements.txt'),
    zip_safe=False,
    entry_points="""
        [console_scripts]
        browsertrix=browsertrix_cli.main:cli
        btrix=browsertrix_cli.main:cli
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
