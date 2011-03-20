#!/usr/bin/env python

# Bootstrap installation of Distribute
import distribute_setup
distribute_setup.use_setuptools()

import os

from setuptools import setup

PROJECT = u'BDD on decorators'
VERSION = '0.1'
URL = 'https://github.com/denz/bdd-experiment'
AUTHOR = u'Denis Mishchishin'
AUTHOR_EMAIL = u'dennz78@gmail.com'
DESC = "Decorators based BDD testing with extended stages set - given-when-then-should"

def read_file(file_name):
    file_path = os.path.join(
        os.path.dirname(__file__),
        file_name
        )
    return open(file_path).read()


setup(
    name=PROJECT,
    version=VERSION,
    description=DESC,
    long_description=read_file('README.rst'),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=read_file('LICENSE'),
    namespace_packages=[],
    packages=['bdd',],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
    	# see http://pypi.python.org/pypi?:action=list_classifiers
        # -*- Classifiers -*- 
        'License :: OSI Approved',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing'
    ],
)
