#!/usr/bin/env python
"""
Plays two or more camera files simultaneously
Michael Hirsch
Updated Aug 2015 to handle HDF5 user-friendly huge video file format

examples:
./RunSimulFrame -i ~/data/2013-04-14/HST/2013-04-14T8-54_hst0.h5 ~/data/2013-04-14/HST/2013-04-14T8-54_hst1.h5 -t 2013-04-14T08:54:25Z 2013-04-14T08:54:30Z
./RunSimulFrame -i ~/data/2013-04-14/hst/2013-04-14T1034_hst1.h5 -c cal/hst1cal.h5 -s -0.1886792453
"""
import matplotlib
matplotlib.use('Agg')
#
import logging
logging.basicConfig(level=logging.WARN)
from dateutil.parser import parse
#
from histutils import Path
from histfeas.camclass import Cam
from histutils.simulFrame import getSimulData
from histutils.plotsimul import plotRealImg

climperc = (1,99.9) #for auto-contrast

def getmulticam(flist,tstartstop,cpar,outdir,cals):
#%%
    dpath = Path(flist[0]).expanduser().parent
    sim = Sim(dpath,tstartstop)
#%% cams
    if len(cals) != len(flist):
        cals=[None]*len(flist)

    cam = []
    for i,(f,c) in enumerate(zip(flist,cals)):
        cpar['fn'] = f + ','
        cam.append(Cam(sim,cpar,i,calfn=c))

    sim.kineticsec = min([C.kineticsec for C in cam]) #playback only, arbitrary
#%% extract data
    cam,rawdata,sim = getSimulData(sim,cam)
#%% plot data
    for t in range(sim.nTimeSlice):
        plotRealImg(sim,cam,rawdata,t,odir=outdir)
#%% classdef
class Sim:
    def __init__(self,dpath,tstartstop):
        try:
            self.startutc = parse(tstartstop[0])
            self.stoputc  = parse(tstartstop[1])
        except (TypeError,AttributeError): #no specified time
            print('loading all frames')

        self.raymap = 'astrometry'
        self.realdata = True
        self.realdatapath = dpath

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='plays two or more cameras at the same time')
    p.add_argument('-i','--flist',help='list of files to play at the same time',nargs='+',required=True)
    p.add_argument('-t','--tstartstop',metavar=('start','stop'),help='start stop time to play yyyy-mm-ddTHH:MM:SSZ',nargs=2)
    p.add_argument('-o','--outdir',help='output directory',default='.')
    p.add_argument('-c','--clist',help='list of calibration file for each camera',nargs='+',default=[])
    p.add_argument('-s','--toffs',help='time offset [sec] to account for camera drift',type=float,nargs='+',required=True)
    p = p.parse_args()

    cpar = {'nCutPix':'512,',
            'timeShiftSec':p.toffs}

    getmulticam(p.flist,p.tstartstop,cpar,p.outdir,p.clist)
