#!/usr/bin/env python3
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
#
from walktree import walktree

def readCalFITS(indir,azfn,elfn):
    flist = walktree(indir)
    az,el = readazelfits(azfn,elfn)
    img = readFITS(flist,az,el)

    return img,az,el
    
def readazelfits(azfn,elfn):
    """
    reads one-time spatial calibration (plate scale) of DASC all-sky camera.
    """
    

def readFITS(flist,azmap,elmap):
    
    header = fits.open(flist[0])
    img = header[0].data
    data = np.zeros((img.size,len(flist)))
    dataloc = np.zeros((img.size,3))  
    times = np.zeros((len(flist),2))
    for i in range(len(flist)):
        try:
            fn = flist[i]
            fund = fn.find('PKR')
            date = (datetime(int(fn[fund+14:fund+18]),int(fn[fund+18:fund+20]),int(fn[fund+20:fund+22]),int(fn[fund+23:fund+25]),int(fn[fund+25:fund+27]),int(fn[fund+27:fund+29]))-datetime(1970,1,1,0,0,0)).total_seconds()
            times[i] = [date,date+1]
            header = fits.open(fn)
            img = header[0].data
            data[:,i] = img.flatten()
        except:
            print fn,'has error'
    data = {'image':data}    
        
    coordnames="spherical"
    
    az = fits.open(azmap)[0].data
    el = fits.open(elmap)[0].data
    dataloc[:,0] = 135 # in km, this is an assumtion, john take note
    dataloc[:,1] = az.flatten()
    dataloc[:,2] = el.flatten()
    
    sensorloc=np.array([65,-148,0])
        
    return data,coordnames,dataloc,sensorloc,times
    
if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='for Poker Flat DASC all sky camera, read az/el mapping and images')
    p.add_argument('indir',help='directory of .fits or specific .fits file')
    p.add_argument('azfn',help='filename for DASC .fits azimuth calibration')
    p.add_argument('elfn',help='filename for DASC .fits elevation calibration')  
    p=p.parse_args()


    img,az,el = readFITS(p.indir,p.azfn,p.elfn)
    