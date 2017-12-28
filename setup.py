#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='ptime',
    version='0.1.7',
    url='http://github.com/Ibadinov/ptime',
    license='MIT',
    author='Marat Ibadinov',
    author_email='ibadinov@me.com',

    platforms='any',
    install_requires=['pytz', 'python-dateutil'],
    packages=['ptime', 'ptime.languages'],
    package_data={
        '': ['*.json']
    },
    zip_safe=False,
    test_suite='tests'
)
