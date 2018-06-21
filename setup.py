#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = ['python-dateutil', 'pytz', 'numpy', 'scipy', 'h5py', 'astropy',
                    'pymap3d', 'sciencedates']
tests_require = ['pytest', 'coveralls', 'flake8', 'mypy']


setup(name='histutils',
      packages=find_packages(),
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scivision/histutils',
      description='Utilities for reading HiST data, etc.',
      long_description=open('README.md').read(),
      long_description_content_type="text/markdown",
      version='0.9.2',
      classifiers=[
          'Intended Audience :: Science/Research',
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Topic :: Scientific/Engineering :: Atmospheric Science',
          'Programming Language :: Python :: 3.6',
      ],
      install_requires=install_requires,
      python_requires='>=3.6',
      extras_require={'plot': ['tifffile', 'matplotlib', 'seaborn', ],
                      'io': ['dascutils', 'themisasi'],
                      'tests': tests_require},
      tests_require=tests_require,
      scripts=['ConvertDMC2h5.py', 'HDDcost.py', 'Playh5.py', 'RunSimulFrame.py',
               'date2doy.py', 'WhenEnd.py', 'WienerAurora.py'],
      include_package_data=True,
      )
