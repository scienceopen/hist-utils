#!/usr/bin/env python
"""
Plays two or more camera files simultaneously
Michael Hirsch
Updated Aug 2015 to handle HDF5 user-friendly huge video file format

uses data converted from raw .DMCdata format by a command like
./ConvertDMC2h5.py ~/U/irs_archive4/HSTdata/2013-04-14-HST1/2013-04-14T07-00-CamSer1387.DMCdata -s 2013-04-14T07:00:07Z -k 0.0333333333333333 -t 2013-04-14T9:25:00Z 2013-04-14T9:35:00Z -l 65.12657 -147.496908333 210 --rotccw 2 -o ~/data/2013-04-14/hst/2013-04-14T0925_hst1.h5


examples:
./RunSimulFrame.py -i ~/data/2013-04-14/hst/2013-04-14T8-54_hst0.h5 ~/data/2013-04-14/HST/2013-04-14T8-54_hst1.h5 -t 2013-04-14T08:54:25Z 2013-04-14T08:54:30Z

./RunSimulFrame.py -i ~/data/2013-04-14/hst/2013-04-14T1034_hst1.h5 -c cal/hst1cal.h5 -s -0.1886792453 --cmin 1050 --cmax 1150 -m 77.5 19.9
./RunSimulFrame.py  -i ~/data/2013-04-14/hst/2013-04-14T1034_hst0.h5 ~/data/2013-04-14/hst/2013-04-14T1034_hst1.h5 -c cal/hst0cal.h5 cal/hst1cal.h5 -s -0.1886792453 0 --cmin 100 1025 --cmax 2000 1130 -m 77.5 19.9 -t 2013-04-14T10:34:25Z 2013-04-14T10:35:00Z

./RunSimulFrame.py  -i ~/data/2013-04-14/hst/2013-04-14T0925_hst1.h5 -c cal/hst1cal.h5 --cmin 1025 --cmax 1130 -t 2013-04-14T09:27Z 2013-04-14T09:30Z -s 0
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.animation as anim
from matplotlib.pyplot import figure
#
from six import string_types
from datetime import datetime
from numpy import arange
import logging
logging.basicConfig(level=logging.WARN)
from dateutil.parser import parse
#
from histutils import Path
from histfeas.camclass import Cam
from histutils.simulFrame import getSimulData,HSTframeHandler
from histutils.plotsimul import plotRealImg

DPI = 100

def getmulticam(flist,tstartstop,framereq,cpar,odir,cals):
#%%
    flist = [Path(f) for f in flist]
    dpath = flist[0].expanduser().parent
    fnlist=[]
    for f in flist:
        fnlist.append(f.name)
    cpar['fn'] = ','.join(fnlist)

    sim = Sim(dpath,tstartstop,framereq)
#%% cams
    if len(cals) != len(flist):
        cals=[None]*len(flist)

    cam = []
    for i,c in enumerate(cals):
        cam.append(Cam(sim,cpar,i,calfn=c))

    sim.kineticsec = min([C.kineticsec for C in cam]) #playback only, arbitrary
#%% extract data
    if hasattr(sim,'pbInd'): #one camera, specified indices
        cam[0].pbInd = sim.pbInd
        cam, rawdata = HSTframeHandler(sim,cam)
    else:
        cam,rawdata,sim = getSimulData(sim,cam)
#%% make movie
    ofn = Path(odir).expanduser() / flist[0].with_suffix('.mkv').name
    print('writing {}'.format(ofn))

    fg = figure()
    Writer = anim.writers['ffmpeg']
    writer = Writer(fps=15, codec='ffv1') # ffv1 is lossless codec. Omitting makes smeared video
    with writer.saving(fg,str(ofn),DPI):
        for t in range(sim.nTimeSlice):
            plotRealImg(sim,cam,rawdata,t,odir=None,fg=fg) #odir=None stops png writing
            writer.grab_frame(facecolor='k')
            if not t % 200: print('{}/{}'.format(t,sim.nTimeSlice))
#%% classdef
class Sim:
    def __init__(self,dpath,tstartstop,framereq):
        try:
            if isinstance(tstartstop[0],string_types):
                self.startutc = parse(tstartstop[0])
                self.stoputc  = parse(tstartstop[1])
            elif framereq[0] is not None:
                self.pbInd = arange(framereq[0],framereq[1],framereq[2]) #NOT range
                self.nTimeSlice = self.pbInd.size
            else:
                raise TypeError
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
    p.add_argument('-t','--tstartstop',metavar=('start','stop'),help='start stop time to play yyyy-mm-ddTHH:MM:SSZ',nargs=2,default=[None])
    p.add_argument('-f','--frames',metavar=('start','stop','step'),help='start stop step frame indices to play',nargs=3,type=int)
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

    getmulticam(p.flist,p.tstartstop,p.frames,cpar,p.outdir,p.clist)
