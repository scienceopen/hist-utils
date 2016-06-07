#!/usr/bin/env python3
import os,sys
from setuptools import setup
import subprocess

exepath = os.path.dirname(sys.executable)
try:
    subprocess.call([os.path.join(exepath,'conda'),'install','--yes','--file','requirements.txt'])
except Exception as e:
    print('tried conda in {}, but you will need to install packages in requirements.txt  {}'.format(exepath,e))


with open('README.rst','r') as f:
	long_description = f.read()

setup(name='histutils',
      packages=['histutils'],
	  description='utilities for the HiST auroral tomography system',
	  long_description=long_description,
	  author='Michael Hirsch',
	  url='https://github.com/scienceopen/histutils',
	  install_requires=['tifffile',
			            'pymap3d','dmcutils'],
   dependency_links = [
        'https://github.com/scienceopen/pymap3d/tarball/master#egg=pymap3d',
        'https://github.com/scienceopen/dmcutils/tarball/master#egg=dmcutils',
        ],
	  )


