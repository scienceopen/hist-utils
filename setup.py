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
	  install_requires=['tifffile','pathvalidate','pymap3d'],
	  )

