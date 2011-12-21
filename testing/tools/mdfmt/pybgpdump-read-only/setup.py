#!/usr/bin/env python

from distutils.core import setup

setup(name='pybgpdump',
      version = '0.2',
      license = 'GPL',
      author = 'Jon Oberheide',
      author_email = 'jon@oberheide.org',
      url = 'http://jon.oberheide.org/projects/pybgpdump/',
      description = 'pybgpdump combines the functionality of libbgpdump and the ease of python to parse BGP messages from MRT dumps.',
      py_modules = [ 'pybgpdump' ])
