#!/usr/bin/env python
from setuptools import setup
import subprocess

try:
    subprocess.call(['conda','install','--file','requirements.txt'])
except Exception as e:
    pass

setup(name='histutils',
      packages=['histutils'],
	  description='utilities for the HiST auroral tomography system',
	  author='Michael Hirsch',
	  url='https://github.com/scienceopen/histutils',
	  install_requires=['tifffile','pathvalidate',
			            'pymap3d','dmcutils'],
      dependency_links = [
        'https://github.com/scienceopen/pymap3d/tarball/master#egg=pymap3d',
        'https://github.com/scienceopen/dmcutils/tarball/master#egg=dmcutils',
        ],
	  )


