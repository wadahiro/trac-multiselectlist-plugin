#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

PACKAGE = 'MiltiSelectListPlugin'
VERSION = '0.0.1'

setup(
    name=PACKAGE, version=VERSION,
    description='It enables it to perform multiple selection in the item Select.',
    author="", author_email="",
    license='NewBSD', url='',
    zip_safe=True,
    packages = ['multiselectlist'],
    entry_points = {
        'trac.plugins': [
            'multiselectlist.multiselectlist = multiselectlist.multiselectlist',
        ]
    }
)
