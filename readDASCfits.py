#!/usr/bin/env python3
"""
Reads DASC allsky cameras images in FITS formats into GeoData. Can also run standalone.
To download DASC images using Octave, Matlab, or Python checkout:
https://github.com/jswoboda/ISR_Toolbox/blob/master/Allsky/dlFITS.m
"""
from astropy.io import fits
import numpy as np
from dateutil.parser import parse
from datetime import datetime
from warnings import warn
#
from walktree import walktree

def readCalFITS(indir,azfn,elfn):
    flist = walktree(indir,"*.fits")
    data,coordnames,dataloc,sensorloc,times = readFITS(flist,azfn,elfn)
    try:
        return data['image']  
    except:
        return None     

def readFITS(flist,azfn,elfn):
    """
    reads FITS images and spatial az/el calibration for allsky camera
    """
    if not flist:
        warn('no data files found')
        return (None,)*5
#%% preallocate, assuming all images the same size        
    with fits.open(flist[0],mode='readonly') as h:
        img = h[0].data
    dataloc = np.empty((len(flist),3))  
    times =   np.empty((len(flist),2))
    img =     np.zeros((len(flist),img.shape[0],img.shape[1]),img.dtype) #zeros in case a few images fail to load
    epoch = datetime(1970,1,1,0,0,0)
#%% iterate over image files    
    for i,fn in enumerate(flist):
        try:
            with fits.open(fn,mode='readonly') as h:
                expstart_dt = parse(h[0].header['OBSDATE'] + ' ' + h[0].header['OBSSTART'])
                expstart_unix = (expstart_dt - epoch).total_seconds()
                times[i,:] = [expstart_unix,expstart_unix + h[0].header['EXPTIME']]
                img[i,...] = h[0].data             
        except Exception as e:
            print(fn+ 'has error {}'.format(e))
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
    
    sensorloc=np.array([65,-148,0])
        
    return data,coordnames,dataloc,sensorloc,times
    
if __name__ == '__main__':
    import cv2 # easy way to show fast movie
    
    from argparse import ArgumentParser
    p = ArgumentParser(description='for Poker Flat DASC all sky camera, read az/el mapping and images')
    p.add_argument('indir',help='directory of .fits or specific .fits file')
    p.add_argument('azfn',help='filename for DASC .fits azimuth calibration',nargs='?')
    p.add_argument('elfn',help='filename for DASC .fits elevation calibration',nargs='?')  
    p=p.parse_args()


    img = readCalFITS(p.indir,p.azfn,p.elfn)
#%% play movie   
    for I in img:
        cv2.imshow('DASC',I)
        cv2.pause(0.01)
    