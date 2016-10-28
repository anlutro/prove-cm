#!/usr/bin/env python3

from __future__ import print_function
from setuptools import setup, find_packages
import sys

if sys.version_info[0] != 3:
    print('Only Python 3 is supported!')
    sys.exit(1)

setup(
    name='prove',
    packages=find_packages(include=['prove', 'prove.*']),
    license='MIT',
    author='Andreas Lutro',
    author_email='anlutro@gmail.com',
    install_requires=[
        'allib',
        'mako',
        'paramiko',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'prove=prove.client.console:main',
            'prove-agent=prove.client.agent:main',
        ],
    },
)
