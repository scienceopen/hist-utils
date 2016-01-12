#!/usr/bin/env python3
"""
Reads DASC allsky cameras images in FITS formats into GeoData.
Run standalone from PlayDASC.py
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

EPOCH = datetime(1970,1,1,0,0,0,tzinfo=UTC)

def readCalFITS(indir,azfn,elfn,wl=[]):
    indir = Path(indir).expanduser()
    if not wl:
        wl += '*' #select all wavelengths

    flist = []
    for w in wl:
        flist += sorted(indir.glob("PKR_DASC_0{}_*.FITS".format(w)))
    return readFITS(flist,azfn,elfn)

def readFITS(flist,azfn,elfn,heightkm=135):
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
    times =   np.empty((len(flist),2)); times.fill(np.nan)
    img =     np.zeros((len(flist),img.shape[0],img.shape[1]),img.dtype) #zeros in case a few images fail to load
    wavelen = np.empty(len(flist)); wavelen.fill(np.nan)
#%% iterate over image files
    for i,fn in enumerate(flist):
        try:
            with fits.open(str(fn),mode='readonly') as h:
                expstart_dt = forceutc(parse(h[0].header['OBSDATE'] + ' ' + h[0].header['OBSSTART']))
                expstart_unix = (expstart_dt - EPOCH).total_seconds()
                times[i,:] = [expstart_unix,expstart_unix + h[0].header['EXPTIME']]

                wavelen[i] = h[0].header['FILTWAV']

                img[i,...] = h[0].data
        except Exception as e:
            print('{} has error {}'.format(fn,e))
    data = {'image':img,'lambda':wavelen}

    coordnames="spherical"
    try:
        azfn = Path(azfn).expanduser()
        elfn = Path(elfn).expanduser()
        with fits.open(str(azfn),mode='readonly') as h:
            az = h[0].data
        with fits.open(str(elfn),mode='readonly') as h:
            el = h[0].data
        dataloc[:,0] = heightkm
        dataloc[:,1] = az.ravel()
        dataloc[:,2] = el.ravel()
    except Exception as e:
        warn('could not read az/el mapping.   {}'.format(e))
        dataloc=None

    sensorloc=np.array([65.13,-147.47,0]) #NOTE should be approx. true for Poker DASC

    return data,coordnames,dataloc,sensorloc,times