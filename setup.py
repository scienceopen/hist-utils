#!/usr/bin/env python3

from setuptools import setup 

with open('README.rst') as f:
	long_description = f.read()
	
setup(name='histutils',
      version='0.1',
	  description='utilities for the HiST auroral tomography system',
	  long_description=long_description,
	  author='Michael Hirsch',
	  author_email='hirsch617@gmail.com',
	  url='https://github.com/scienceopen/histutils',
	  install_requires=['scipy','scikit-image','h5py','astropy','matplotlib','six','nose'],
      packages=['histutils'],
	  )

#dependency_links = ['https://github.com/scienceopen/gaussfitter/master#egg=gaussfitter']
	  	  
