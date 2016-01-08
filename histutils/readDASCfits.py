#!/usr/bin/env python3
"""
Reads DASC allsky cameras images in FITS formats into GeoData.
Run standalone from PlayDASC.py

To download DASC images using Octave, Matlab, or Python checkout:
https://github.com/jswoboda/ISR_Toolbox/blob/master/Allsky/dlFITS.m
or
download manually from
https://amisr.asf.alaska.edu/PKR/DASC/RAW/
note the capitalization is required in that URL.
"""
from pathlib import Path
from astropy.io import fits
import numpy as np
from dateutil.parser import parse
from datetime import datetime
from warnings import warn
from pytz import UTC
#
from histutils.fortrandates import forceutc

def readCalFITS(indir,azfn,elfn):
    indir = Path(indir).expanduser()
    pats = ["PKR_DASC_*.fits","PKR_DASC_*.FITS"]

    flist = []
    for p in pats:
        flist += sorted(indir.glob(p))
    return readFITS(flist,azfn,elfn)

def readFITS(flist,azfn,elfn):
    """
    reads FITS images and spatial az/el calibration for allsky camera
    """
    if not flist:
        warn('no data files found')
        return
#%% preallocate, assuming all images the same size
    with fits.open(str(flist[0]),mode='readonly') as h:
        img = h[0].data
    dataloc = np.empty((img.size,3))
    times =   np.empty((len(flist),2))
    img =     np.zeros((len(flist),img.shape[0],img.shape[1]),img.dtype) #zeros in case a few images fail to load
    epoch = datetime(1970,1,1,0,0,0,tzinfo=UTC)
#%% iterate over image files
    for i,fn in enumerate(flist):
        try:
            with fits.open(str(fn),mode='readonly') as h:
                expstart_dt = forceutc(parse(h[0].header['OBSDATE'] + ' ' + h[0].header['OBSSTART']))
                expstart_unix = (expstart_dt - epoch).total_seconds()
                times[i,:] = [expstart_unix,expstart_unix + h[0].header['EXPTIME']]
                img[i,...] = h[0].data
        except Exception as e:
            print('{} has error {}'.format(fn,e))
    data = {'image':img}

    coordnames="spherical"
    try:
        with fits.open(azfn,mode='readonly') as h:
            az = h[0].data
        with fits.open(elfn,mode='readonly') as h:
            el = h[0].data
        dataloc[:,0] = 135 #NOTE in km, this is an assumtion, john take note
        dataloc[:,1] = az.ravel()
        dataloc[:,2] = el.ravel()
    except Exception as e:
        warn('could not read az/el mapping.   {}'.format(e))
        dataloc=None

    sensorloc=np.array([65.13,-147.47,0])

    return data,coordnames,dataloc,sensorloc,times