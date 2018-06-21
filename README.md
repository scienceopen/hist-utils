[![image](https://travis-ci.org/scivision/histutils.svg?branch=master)](https://travis-ci.org/scivision/histutils)
[![image](http://coveralls.io/repos/scivision/histutils/badge.svg?branch=master&service=github)](http://coveralls.io/github/scivision/histutils?branch=master)
[![Maintainability](https://api.codeclimate.com/v1/badges/a40627d049d2f3168ae0/maintainability)](https://codeclimate.com/github/scivision/histutils/maintainability)
[![pypi versions](https://img.shields.io/pypi/pyversions/histutils.svg)](https://pypi.python.org/pypi/histutils)
[![pypi format](https://img.shields.io/pypi/format/histutils.svg)](https://pypi.python.org/pypi/histutils)
[![PyPi Download stats](http://pepy.tech/badge/histutils)](http://pepy.tech/project/histutils)


# HiST Utils

HiST project raw video data reading utilities.

## Install

    python -m pip install -e .

## User Programs/Scripts

These functions are primarily made to be used from the Terminal by a
human, they implement a complete program using the module functions.

### RunSimulPlay

Simultaneous video playback of two or more cameras.

* -i input file list (.h5) 
* -t Time range start/stop 
* -o Output directory for plots (optional, slow)

#### Example

```bash
$ python RunSimulFrame.py -i ~/data/cmos2013-01-14T1-15.h5 ~/data/ccd2013-01-14T1-15.h5
```

using the [data from January 13, 2013
experiment](http://heaviside.bu.edu/~mhirsch/dmc/2013-01-13/) during
active plasma time.

### ConvertDMC2h5.py

Typically used by our staff internally to convert our binary .DMCdata
files to human- and fast processing- friendly HDF5 files.

#### Example

    python ConvertDMC2h5.py -p 512 512 -b 1 1 -k 0.0188679245283019 -o testframes_cam0.h5 ~/data/2013-04-14T07-00-CamSer7196_frames_363000-1-369200.DMCdata -s 2013-04-14T06:59:55Z -t 2013-04-14T08:54:10Z 2013-04-14T08:54:10.05Z 

    python ConvertDMC2h5.py -p 512 512 -b 1 1 -k 0.0333333333333333 -o testframes_cam1.h5 ~/data/2013-04-14T07-00-CamSer1387_frames_205111-1-208621.DMCdata -s 2013-04-14T07:00:07Z -t 2013-04-14T08:54:10Z 2013-04-14T08:54:10.05Z

### WhenEnd.py

Just predicts the end of a .DMCdata file "does this file cover the
auroral event time?"

## Module Functions

These functions are typically targeted for calling from other programs,
however, many of these can also be used from the Terminal directly.

## Examples

Many more possibilities exist, the `-h` option on most functions will
give some hints as to what the program can do.

## Reference Examples

These examples are old, now we use HDF5 files. Kept for reference only.

### Read .DMCdata file from within a Python script

    from histutils import rawDMCreader
    data = rawDMCreader.goRead('myfile.DMCdata')[0]

### Using rawDMCreader.py from Terminal

    cd histutils/histutils
    python3 rawDMCreader.py ~/data/
