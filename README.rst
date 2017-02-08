.. image:: https://travis-ci.org/scienceopen/histutils.svg?branch=master
    :target: https://travis-ci.org/scienceopen/histutils
.. image:: http://coveralls.io/repos/scienceopen/histutils/badge.svg?branch=master&service=github
   :target: http://coveralls.io/github/scienceopen/histutils?branch=master

==========
HiSTutils
==========

:Author: Michael Hirsch
:License: GPLv3+

HiST project raw video data reading utilities.

.. contents::

Install
=======
::
  
  python setup.py develop

User Programs/Scripts
=====================
These functions are primarily made to be used from the Terminal by a human, they
implement a complete program using the module functions.

RunSimulPlay
------------
Simultaneous video playback of two or more cameras.

-i    input file list (.h5)
-t    Time range start/stop
-o    Output directory for plots (optional, slow)

Example
~~~~~~~

.. code:: bash

  $ python RunSimulFrame.py -i ~/data/cmos2013-01-14T1-15.h5 ~/data/ccd2013-01-14T1-15.h5

using the `data from January 13, 2013 experiment <http://heaviside.bu.edu/~mhirsch/dmc/2013-01-13/>`_ during active plasma time.

ConvertDMC2h5.py
----------------
Typically used by our staff internally to convert our binary .DMCdata files to human- and fast processing- friendly HDF5 files.

Example
~~~~~~~
::

 python ConvertDMC2h5.py -p 512 512 -b 1 1 -k 0.0188679245283019 -o testframes_cam0.h5 ~/data/2013-04-14T07-00-CamSer7196_frames_363000-1-369200.DMCdata -s 2013-04-14T06:59:55Z -t 2013-04-14T08:54:10Z 2013-04-14T08:54:10.05Z 

 python ConvertDMC2h5.py -p 512 512 -b 1 1 -k 0.0333333333333333 -o testframes_cam1.h5 ~/data/2013-04-14T07-00-CamSer1387_frames_205111-1-208621.DMCdata -s 2013-04-14T07:00:07Z -t 2013-04-14T08:54:10Z 2013-04-14T08:54:10.05Z

WhenEnd.py
----------
Just predicts the end of a .DMCdata file "does this file cover the auroral event time?"


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

  rawDMCreader            Reads .DMCdata files output by the DMC and HiST networked optical auroral observation systems
  getRawInd               for ``.DMCdata`` video files, lists the first and last raw frame indices in file
  normframe               Given an 8-bit, 16-bit, or float image, normalize to [0..1] data range
  sixteen2eight           converts a 16-bit image to 8-bit image

  plotSolarElev           Computes solar elevation angle and solar irradience vs. time/date for a given location on Earth
  h5lister                recursively list paths and variables in HDF5 file

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
::

    from histutils import rawDMCreader
    data = rawDMCreader.goRead('myfile.DMCdata')[0]

Using rawDMCreader.py from Terminal
-----------------------------------
::

    cd histutils/histutils
    python3 rawDMCreader.py ~/data/
