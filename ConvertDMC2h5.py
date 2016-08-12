#!/usr/bin/env python
"""
Converts 2011 Poker/Ester and 2013-2016 HiST raw data files to HDF5 for easy consumption

full command example with metadata:
./ConvertDMC2h5.py ~/U/irs_archive3/HSTdata/2013-04-14-HST0/2013-04-14T07-00-CamSer7196.DMCdata \
  -s 2013-04-14T06:59:55Z -k 0.018867924528301886 -t 2013-04-14T11:30:00Z 2013-04-14T11:30:02Z \
  -o /tmp/2013-04-14T113000_hst0.h5 -l 65.1186367 -147.432975 500

simple command example w/o full metadata (can append metadata later):
./ConvertDMC2h5.py 2011-03-01T1000/010311.100608.000.dat -o /tmp/2013-03-11T1006.h5 --headerbytes 0
"""

from sys import argv
from numpy import int64
#
from histutils.rawDMCreader import goRead
from histutils.vid2h5 import vid2h5
from histutils.plots import doPlayMovie,doplotsave

if __name__ == "__main__":
    from argparse import ArgumentParser
    p = ArgumentParser(description='Raw .DMCdata file reader, plotter, converter')
    p.add_argument('infile',help='.DMCdata file name and path')
    p.add_argument('-p','--pix',help='nx ny  number of x and y pixels respectively',nargs=2,default=(512,512),type=int)
    p.add_argument('-b','--bin',help='nx ny  number of x and y binning respectively',nargs=2,default=(1,1),type=int)
    p.add_argument('-f','--frames',help='frame indices of file (not raw)',nargs=3,metavar=('start','stop','stride'), type=int64) #don't use string
    p.add_argument('-m','--movie',help='seconds per frame. ',type=float)
    p.add_argument('-c','--clim',help='min max   values of intensity expected (for contrast scaling)',nargs=2,type=float)
    p.add_argument('-k','--kineticsec',help='kinetic rate of camera (sec)  = 1/fps',type=float)
    p.add_argument('--rotccw',help='rotate CCW value in 90 deg. steps',type=int,default=0)
    p.add_argument('--transpose',help='transpose image',action='store_true')
    p.add_argument('--flipud',help='vertical flip',action='store_true')
    p.add_argument('--fliplr',help='horizontal flip',action='store_true')
    p.add_argument('-s','--startutc',help='utc time of nights recording')
    p.add_argument('-t','--ut1',help='UT1 times (seconds since Jan 1 1970) to request (parseable string, int, or float)',metavar=('start','stop'),nargs=2)
    p.add_argument('-o','--output',help='extract raw data into this file [h5,fits,mat]')
    p.add_argument('--avg',help='return the average of the requested frames, as a single image',action='store_true')
    p.add_argument('--hist',help='makes a histogram of all data frames',action='store_true')
    p.add_argument('-v','--verbose',help='debugging',action='count',default=0)
    p.add_argument('--cmos',help='start stop raw frame of CMOS file',nargs=2,metavar=('firstrawind','lastrawind'),type=int,default=(None,)*2)
    p.add_argument('--fire',help='fire filename')
    p.add_argument('-l','--loc',help='lat lon alt_m of sensor',type=float,nargs=3)
    p.add_argument('--headerbytes',help='number of header bytes: 2013-2016: 4  2011: 0',type=int,default=4)
    p = p.parse_args()

    cmosinit = {'firstrawind':p.cmos[0],'lastrawind':p.cmos[1]}

    params = {'kineticsec':p.kineticsec,'rotccw':p.rotccw,'transpose':p.transpose,
              'flipud':p.flipud,'fliplr':p.fliplr,'fire':p.fire,'sensorloc':p.loc}

    rawImgData,rawind,finf = goRead(p.infile, p.pix,p.bin,p.frames,p.ut1,
                                    p.kineticsec,p.startutc,cmosinit,p.verbose,p.output,p.headerbytes)
#%% convert
    vid2h5(None,finf['ut1'],rawind,p.output,params,argv)
#%% plots and save
    try:
        from matplotlib.pyplot import show
        doPlayMovie(rawImgData,p.movie, ut1_unix=finf['ut1'],clim=p.clim)
        doplotsave(p.infile,rawImgData,rawind,p.clim,p.hist,p.avg)
        show()
    except Exception as e:
        print('skipped plotting  {}'.format(e))
