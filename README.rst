.. image:: https://codeclimate.com/github/scienceopen/histutils/badges/gpa.svg
   :target: https://codeclimate.com/github/scienceopen/histutils
   :alt: Code Climate
.. image:: https://landscape.io/github/scienceopen/histutils/master/landscape.svg?style=flat
   :target: https://landscape.io/github/scienceopen/histutils/master
   :alt: Code Health
.. image:: https://travis-ci.org/scienceopen/histutils.svg?branch=master
    :target: https://travis-ci.org/scienceopen/histutils
.. image:: http://coveralls.io/repos/scienceopen/histutils/badge.svg?branch=master&service=github
   :target: http://coveralls.io/github/scienceopen/histutils?branch=master



HiSTutils
==========

HiST project raw video data reading utilities.

These programs are designed to be platform/OS agnostic.
That is, from Windows, Mac, or Linux:

* ``.m`` files should be callable from Matlab, Octave, or Python using Oct2Py.
* ``.py`` files should be callable from Python 2.7 / 3.4+ or Matlab R2014b+ using the ``py`` module of Matlab

Install
--------------
From Terminal::

  git clone --depth 1 https://github.com/scienceopen/histutils
  conda install --file requirements.txt

Utilities
---------

=============  ===========
Function       Description
=============  ===========
memfree        Estimates available RAM for Matlab/Octave under Windows, Mac, Linux
checkRAM       check if a proposed N-D array with fit in available RAM (w/o swap)
isoctave       detect if ``.m`` code is being run under GNU Octave (vs. Matlab)

cp_parents     Copies files to target, making directories as needed in Python. like ``cp --parents`` in Bash
empty_file     creates/overwrites empty file in Python, make directories as needed. Like ``>myfile`` in Bash
walktree       recursive filename search in Python like GNU Find in Bash

rawDMCreader   Reads .DMCdata files output by the DMC and HiST networked optical auroral observation systems
getRawInd      for ``.DMCdata`` video files, lists the first and last raw frame indices in file
findstars      detects stars and plots detections in image
normframe      Given an 8-bit, 16-bit, or float image, normalize to [0..1] data range
sixteen2eight  converts a 16-bit image to 8-bit image

plotSolarElev  Computes solar elevation angle and solar irradience vs. time/date for a given location on Earth
h5lister       recursively list paths and variables in HDF5 file
readDASCfits   reads FITS image data from Univ. Alaska Digital All Sky Cameras and plays movie
=============  ===========
