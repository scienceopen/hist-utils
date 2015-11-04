#!/usr/bin/env python3

from setuptools import setup

with open('README.rst','r') as f:
	long_description = f.read()

setup(name='histutils',
      version='0.1',
	  description='utilities for the HiST auroral tomography system',
	  long_description=long_description,
	  author='Michael Hirsch',
	  url='https://github.com/scienceopen/histutils',
	  install_requires=['tifffile','pathlib2'],
      packages=['histutils'],
	  )

