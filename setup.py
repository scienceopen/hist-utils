#!/usr/bin/env python
from setuptools import setup

try:
    import conda.cli
    conda.cli.main('install','--file','requirements.txt')
except Exception as e:
    print(e)
    import pip
    pip.main(['install','-r','requirements.txt'])


setup(name='histutils',
      packages=['histutils'],
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scienceopen/histutils',
      description='Utilities for reading HiST data, etc.',
      version='0.9',
      classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: MIT License',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3.6',
      ],
	  install_requires=['tifffile','pathvalidate','pymap3d','sciencedates'],
	  )

