#!/usr/bin/env python3
"""
Plays two or more camera files simultaneously
Michael Hirsch
Updated Aug 2015 to handle HDF5 user-friendly huge video file formatt
"""
import logging
logging.basicConfig(level=logging.WARN)
from dateutil.parser import parse
from os.path import expanduser
import h5py
from numpy import fliplr,flipud,rot90
from matplotlib.pyplot import draw,pause
#
from histutils.simulFrame import getSimulData
from histutils.plotsimul import plotRealImg

def getmulticam(flist,tstartstop,orient,makeplot,outdir):
#%%
    sim = Sim(tstartstop)

    cam = []
    for i,(f,o) in enumerate(zip(flist,orient)):
        cam.append(Cam(f,o,i))

    sim.kineticsec = min([C.kineticsec for C in cam])
#%% extract data
    cam,rawdata,sim = getSimulData(sim,cam,makeplot)
#%% plot data
    for t in range(sim.nTimeSlice):
        plotRealImg(sim,cam,rawdata,t,makeplot,figh=1,outdir=outdir)
        draw()
        pause(0.01)

#%% classdef
class Sim:
    def __init__(self,tstartstop):
        try:
            self.startutc = parse(tstartstop[0])
            self.stoputc  = parse(tstartstop[1])
        except (TypeError,AttributeError): #no specified time
            pass

class Cam:
    def __init__(self,fn,orient,name):
        self.name = name
        self.fn = expanduser(fn)

        with h5py.File(self.fn,'r',libver='latest') as f:
            self.filestartutc = f['/ut1_unix'][0]
            self.filestoputc  = f['/ut1_unix'][-1]
            self.ut1unix      = f['/ut1_unix'].value
            self.kineticsec   = f['/kineticsec'].value
            self.supery,self.superx = f['/rawimg'].shape[1:]

        self.nCutPix = self.supery

        self.rotccw =    orient['rotccw']
        self.transpose = orient['transpose']
        self.flipLR =    orient['fliplr']
        self.flipUD =    orient['fliplr']

        self.clim   = orient['clim']

    def ingestcamparam(self,sim):
        pass

    def doorientimage(self,frame):
        if self.transpose:
            frame = frame.transpose(0,2,1)
        # rotate -- note if you use origin='lower', rotCCW -> rotCW !
        if self.rotccw != 0:
            if frame.ndim==3:
                for f in frame:
                    f = rot90(f,k=self.rotccw)
            elif frame.ndim==2:
                frame = rot90(frame,k=self.rotccw)
        # flip
        if self.flipLR:
            frame = fliplr(frame)
        if self.flipUD:
            frame = flipud(frame)
        return frame

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='plays two or more cameras at the same time')
    p.add_argument('-i','--flist',help='list of files to play at the same time',nargs='+')
    p.add_argument('-t','--tstartstop',metavar=('start','stop'),help='start stop time to play yyyy-mm-ddTHH:MM:SSZ',nargs=2)
    p.add_argument('-o','--outdir',help='output directory')
    p = p.parse_args()

    cpar =[{'rotccw':0,'transpose':False,'fliplr':False,'flipud':False,'clim':(1000,7500)},
           {'rotccw':0,'transpose':False,'fliplr':False,'flipud':False,'clim':(100,1500)}]

    makeplot=[]

    getmulticam(p.flist,p.tstartstop,cpar,makeplot,p.outdir)