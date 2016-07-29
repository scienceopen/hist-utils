#!/usr/bin/env python
"""
Plays two or more camera files simultaneously
Michael Hirsch
Updated Aug 2015 to handle HDF5 user-friendly huge video file format

examples:
./RunSimulFrame.py -i ~/data/2013-04-14/hst/2013-04-14T8-54_hst0.h5 ~/data/2013-04-14/HST/2013-04-14T8-54_hst1.h5 -t 2013-04-14T08:54:25Z 2013-04-14T08:54:30Z
./RunSimulFrame.py -i ~/data/2013-04-14/hst/2013-04-14T1034_hst1.h5 -c cal/hst1cal.h5 -s -0.1886792453 --cmin 1050 --cmax 1150 -m 77.5 19.9
./RunSimulFrame.py  -i d:/data/2013-04-14/hst/2013-04-14T1034_hst0.h5 d:/data/2013-04-14/hst/2013-04-14T1034_hst1.h5 -c cal/hst0cal.h5 cal/hst1cal.h5 -s -0.1886792453 0 --cmin 100 1025 --cmax 2000 1130 -m 77.5 19.9 -t 2013-04-14T10:34:25Z 2013-04-14T10:35:00Z
"""
import matplotlib
matplotlib.use('Agg')
#
from datetime import datetime
import logging
logging.basicConfig(level=logging.WARN)
from dateutil.parser import parse
#
from histutils import Path
from histfeas.camclass import Cam
from histutils.simulFrame import getSimulData
from histutils.plotsimul import plotRealImg

def getmulticam(flist,tstartstop,cpar,outdir,cals):
#%%
    flist = [Path(f) for f in flist]
    dpath = flist[0].expanduser().parent
    fnlist=[]
    for f in flist:
        fnlist.append(f.name)
    cpar['fn'] = ','.join(fnlist)

    sim = Sim(dpath,tstartstop)
#%% cams
    if len(cals) != len(flist):
        cals=[None]*len(flist)

    cam = []
    for i,c in enumerate(cals):
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

        self.dpi = 60

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='plays two or more cameras at the same time')
    p.add_argument('-i','--flist',help='list of files to play at the same time',nargs='+',required=True)
    p.add_argument('-t','--tstartstop',metavar=('start','stop'),help='start stop time to play yyyy-mm-ddTHH:MM:SSZ',nargs=2)
    p.add_argument('-o','--outdir',help='output directory',default='.')
    p.add_argument('-c','--clist',help='list of calibration file for each camera',nargs='+',default=[])
    p.add_argument('-s','--toffs',help='time offset [sec] to account for camera drift',type=float,nargs='+',required=True)
    p.add_argument('-m','--mag',help='inclination, declination',nargs=2,type=float,default=(None,None))
    p.add_argument('--cmin',help='min data values per camera',nargs='+',type=int,default=(100,100))
    p.add_argument('--cmax',help='max data values per camera',nargs='+',type=int,default=(1200,1200))
    p = p.parse_args()

    cpar = {'nCutPix':'512,512',
            'timeShiftSec':p.toffs,
            'Bincl':p.mag[0],
            'Bdecl':p.mag[1],
            'plotMinVal':p.cmin,
            'plotMaxVal':p.cmax,
            'Bepoch':datetime(2013,4,14,8,54)}

    getmulticam(p.flist,p.tstartstop,cpar,p.outdir,p.clist)
