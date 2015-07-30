#!/usr/bin/env python3
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from warnings import warn
#
from walktree import walktree

def readCalFITS(indir,azfn,elfn):
    flist = walktree(indir,"*.fits")
    data,coordnames,dataloc,sensorloc,times = readFITS(flist,azfn,elfn)

    return data['image']  

def readFITS(flist,azfn,elfn):
    """
    reads FITS images and spatial az/el calibration for allsky camera
    """
    
    header = fits.open(flist[0],mode='readonly')
    img = header[0].data
    #data = np.empty((img.size,len(flist)))
    dataloc = np.empty((img.size,3))  
    times =   np.empty((len(flist),2))
    for i in range(len(flist)):
        try:
            fn = flist[i]
            fund = fn.find('PKR')
            date = (datetime(int(fn[fund+14:fund+18]),
                             int(fn[fund+18:fund+20]),
                             int(fn[fund+20:fund+22]),
                             int(fn[fund+23:fund+25]),
                             int(fn[fund+25:fund+27]),
                             int(fn[fund+27:fund+29]))-datetime(1970,1,1,0,0,0)).total_seconds()
            times[i] = [date,date+1]
            header = fits.open(fn)
            img = header[0].data
            #data[:,i] = img.flatten() #
        except Exception as e:
            print(fn+ 'has error {}'.format(e))
    data = {'image':img}    
        
    coordnames="spherical"
    try:
        az = fits.open(azfn,mode='readonly')[0].data
        el = fits.open(elfn,mode='readonly')[0].data
        dataloc[:,0] = 135 #NOTE in km, this is an assumtion, john take note
        dataloc[:,1] = az.ravel()
        dataloc[:,2] = el.ravel()
    except Exception as e:
        warn('could not read az/el mapping.   {}'.format(e))
        dataloc=None
    
    sensorloc=np.array([65,-148,0])
        
    return data,coordnames,dataloc,sensorloc,times
    
if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='for Poker Flat DASC all sky camera, read az/el mapping and images')
    p.add_argument('indir',help='directory of .fits or specific .fits file')
    p.add_argument('azfn',help='filename for DASC .fits azimuth calibration',nargs='?')
    p.add_argument('elfn',help='filename for DASC .fits elevation calibration',nargs='?')  
    p=p.parse_args()


    img = readCalFITS(p.indir,p.azfn,p.elfn)
    