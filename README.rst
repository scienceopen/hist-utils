.. image:: https://codeclimate.com/github/scienceopen/histutils/badges/gpa.svg
   :target: https://codeclimate.com/github/scienceopen/histutils
   :alt: Code Climate
.. image:: https://landscape.io/github/scienceopen/histutils/master/landscape.svg?style=flat
   :target: https://landscape.io/github/scienceopen/histutils/master
   :alt: Code Health
.. image:: http://coveralls.io/repos/scienceopen/histutils/badge.svg?branch=master&service=github
   :target: http://coveralls.io/github/scienceopen/histutils?branch=master

==========
HiSTutils
==========

:Author: Michael Hirsch
:License: GPLv3+

HiST project raw video data reading utilities.

These programs are designed to be platform/OS agnostic.
That is, from Windows, Mac, or Linux:

* ``.m`` files should be callable from Matlab, Octave, or Python using Oct2Py.
* ``.py`` files should be callable from Python 2.7 / 3.4+ or Matlab R2014b+ using the ``py`` module of Matlab

.. contents::

Install
=======
From Terminal::

  git clone --depth 1 https://github.com/scienceopen/histutils
  conda install --file requirements.txt
  python setup.py develop

User Programs/Scripts
=====================
These functions are primarily made to be used from the Terminal by a human, they
implement a complete program using the module functions.

RunSimulPlay
------------

-i    input file list (.h5)
-t    Time range start/stop
-o    Output directory for plots (optional, slow)

Example
~~~~~~~
.. code:: bash

  $ python RunSimulFrame.py -i ~/data/cmos2013-01-14T1-15.h5 ~/data/ccd2013-01-14T1-15.h5

using the `data from January 13, 2013 experiment <http://heaviside.bu.edu/~mhirsch/dmc/2013-01-13/>`_ during active plasma time.




Module Functions
================
These functions are typically targeted for calling from other programs, however, many
of these can also be used from the Terminal directly.

.. table:: Module Functions

  =====================   ===========
  Function                Description
  =====================   ===========
  findnearest             given array :math:`A`, find indices and values corresponding to scalar :math:`x`
  isoctave                detect if ``.m`` code is being run under GNU Octave (vs. Matlab)

  cp_parents              Copies files to target, making directories as needed in Python -- acts like ``cp --parents`` in Bash
  empty_file              creates/overwrites empty file in Python includes making directories as needed. Like ``>myfile`` in Bash
  walktree                recursive filename search in Python like GNU Find in Bash

  rawDMCreader            Reads .DMCdata files output by the DMC and HiST networked optical auroral observation systems
  getRawInd               for ``.DMCdata`` video files, lists the first and last raw frame indices in file
  findstars               detects stars and plots detections in image
  normframe               Given an 8-bit, 16-bit, or float image, normalize to [0..1] data range
  sixteen2eight           converts a 16-bit image to 8-bit image

  plotSolarElev           Computes solar elevation angle and solar irradience vs. time/date for a given location on Earth
  h5lister                recursively list paths and variables in HDF5 file

  fortrandates.py         conversions between oddball date formats used by classical aeronomy programs in FORTRAN to Python datetime

  diric                   Computes Dirichlet function

  imageconv               convert directory of images to multi-page TIFF
  image_write_multipage   write/read multi-page TIFF

  airMass                 Compute air mass vs. angle (for solar flux compuations)

  timedmc                 Used as part of converting raw DMC data to HDF5 by rawDMCreader
  =====================   ===========




Examples
========
Many more possibilities exist, the ``-h`` option on most functions will give some hints as to what the program can do.


Reference Examples
==================
These examples are old, now we use HDF5 files. Kept for reference only.

Read .DMCdata file from within a Python script
----------------------------------------------
.. code-block:: python

	from histutils import rawDMCreader
	data = rawDMCreader.goRead('myfile.DMCdata')[0]

Using rawDMCreader.py from Terminal
-----------------------------------
.. code-block:: bash

    $ cd histutils/histutils
    $ python3 rawDMCreader.py ~/data/
