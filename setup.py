#!/usr/bin/env python
install_requires= ['python-dateutil', 'pytz','numpy','scipy','h5py', 'astropy',
      'pymap3d','sciencedates']
tests_require=['nose','coveralls']
# %%
from setuptools import setup,find_packages


setup(name='histutils',
      packages=find_packages(),
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
      python_requires='>=3.6',
      extras_require={'plot':['tifffile','matplotlib','seaborn',],
                        'io':['dascutils','themisasi'],
                        'test':tests_require},
      tests_require=tests_require,

	  )

