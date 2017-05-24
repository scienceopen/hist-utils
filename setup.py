#!/usr/bin/env python

req= ['python-dateutil', 'pytz','nose','numpy','scipy','h5py', 'astropy', 'matplotlib','seaborn']

pipreq = ['pathvalidate','pymap3d','sciencedates',]

import pip
try:
    import conda.cli
    conda.cli.main('install',*req)
except ImportError:
    pip.main(['install'] + req)
pip.main(['install'] + pipreq)
# %%
from setuptools import setup


setup(name='histutils',
      packages=['histutils'],
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scivision/histutils',
      description='Utilities for reading HiST data, etc.',
      version='0.9.2',
      classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 3 - Alpha',
      'License :: OSI Approved :: MIT License',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3.6',
      ],
      install_requires=req,
      extras_require={'tifffile':['tifffile'],
                        'dascutils':['dascutils'],
                        'themisasi':['themisasi']},

	  )

