#!/usr/bin/env python
from setuptools import setup

req= ['tifffile','pathvalidate','pymap3d','sciencedates',
      'psutil','python-dateutil','pytz','nose','numpy','scipy','pandas','h5py','astropy','matplotlib','seaborn']


setup(name='histutils',
      packages=['histutils'],
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scienceopen/histutils',
      description='Utilities for reading HiST data, etc.',
      version='0.9.1',
      classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: MIT License',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3.6',
      ],
	  install_requires=req,
	  )

