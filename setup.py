#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from setuptools import setup, find_packages

import rdcli

setup(
    name='rdcli',
    version=rdcli.__version__,
    packages=find_packages(),
    author=rdcli.__author__,
    author_email='contact@mickael-goetz.com',
    description='Use Read-Debrid from your command line !',
    long_description=open('README.rst').read(),
    include_package_data=True,
    url='https://github.com/MrMitch/realdebrid-CLI',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
    ],
    entry_points = {
        'console_scripts': [
            'rdcli = rdcli.rdcli:main',
        ],
    },
    license="WTFPL"
)