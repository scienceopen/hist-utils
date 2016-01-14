#!/usr/bin/env python3
"""
Plots / plays Poker Flat DASC all-sky camera data FITS files

To download DASC images using Octave, Matlab, or Python checkout:
https://github.com/jswoboda/ISR_Toolbox/blob/master/Example_Scripts/loadDASC2013Apr14.py
or
download manually from
https://amisr.asf.alaska.edu/PKR/DASC/RAW/
note the capitalization is required in that URL.
"""
from numpy import arange
from pytz import UTC
from datetime import datetime
from scipy.interpolate import interp1d
from matplotlib.pyplot import show,draw,pause,subplots
from matplotlib.colors import LogNorm
#
from histutils.readDASCfits import readCalFITS

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='for Poker Flat DASC all sky camera, read az/el mapping and images')
    p.add_argument('indir',help='directory of .fits or specific .fits file')
    p.add_argument('-a','--azfn',help='filename for DASC .fits azimuth calibration')
    p.add_argument('-e','--elfn',help='filename for DASC .fits elevation calibration')
    p.add_argument('-w','--wavelength',help='select wavelength(s) to plot simultaneously [428 558 630]',type=int,default=[428,558,630],nargs='+')
    p.add_argument('-m','--minmax',help='set values outside these limits to 0, due to data corruption',type=int,nargs=2,default=[350,7000])
    p.add_argument('-c','--cadence',help='set playback cadence to request times [sec]',type=float,default=5.)
    p=p.parse_args()

    img = []; times = []
    for w in p.wavelength:
        data,coordnames,dataloc,sensorloc,time  = readCalFITS(p.indir,p.azfn,p.elfn,w)
        I = data['image']
        #%% deal with corrupted data
        I[(I<p.minmax[0]) | (I>p.minmax[1])] = 1 #instead of 0 for lognorm
        img.append(I)
        times.append(time)
#%% histogram
    try:
        az = dataloc[:,1].reshape(img[0].shape[1:])
        el = dataloc[:,2].reshape(img[0].shape[1:])
    except Exception: #azel data wasn't loaded
        pass

    fg,axs = subplots(1,3,figsize=(15,5))
    for a,I in zip(axs,img):
        a.hist(I.ravel(),bins=128)
        a.set_yscale('log')
#%% play movie
    fg,axs = subplots(1,3,figsize=(15,5))
    hi = []; ht=[]
    for a,w,x,mm in zip(axs,p.wavelength,(0.25,0.5,0.75),
                     ((350,800),(350,7000),(350,900))):
        a.axis('off')
        fg.text(x,0.05,str(w) + ' nm')
        hi.append(a.imshow(img[0][0],vmin=mm[0],vmax=mm[1],origin='bottom',
                        norm=LogNorm(),cmap='gray'))
        ht.append(a.set_title(''))
        #fg.colorbar(hi[-1],ax=a).set_label('14-bit data numbers')

    T = max([t[0,0] for t in times])
    Tmax = min([t[-1,0] for t in times])
    while T<=Tmax:
        for I,Hi,Ht,t in zip(img,hi,ht,times):
            ft = interp1d(t[:,0],arange(len(t)),kind='nearest')
            ind = ft(T).astype(int)
            #print(ind,end=' ')
            Hi.set_data(I[ind])
            try:
                Ht.set_text(datetime.fromtimestamp(t[ind,0],tz=UTC))
            except OSError: #file had corrupted time
                Ht.set_text('')
        #print(datetime.fromtimestamp(T,tz=UTC))

        draw(); pause(0.05)
        T += p.cadence