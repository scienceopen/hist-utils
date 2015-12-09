"""
functions for loading HST real camera raw data
 michael hirsch 2014, ported from Matlab code

INPUT FILE FORMAT: intended for use with "DMCdata" raw format, 4-byte
 "footer" containing frame index (must use typecast)
"""
from __future__ import division,absolute_import
#from pathlib2 import Path
import logging
from datetime import datetime
from time import time
from pytz import UTC
import h5py
from numpy import arange, unique
from scipy.interpolate import interp1d
# local
from .get1Dcut import get1Dcut

epoch = datetime(1970,1,1,tzinfo=UTC)

def getSimulData(sim,cam,makeplot,progms=None,verbose=0):
#%% synchronize
    cam,sim = HSTsync(sim,cam,verbose)
#%% load 1-D cut slices into keogram array
    cam,rawdata = HSTframeHandler(sim,cam,makeplot,progms,verbose)
    return cam,rawdata,sim

def HSTsync(sim,cam,verbose):
    """ this function now uses UT1 time -- seconds since 1970 Jan 1
    """
    try:
        if isinstance(sim.startutc,datetime):
            reqStart = (sim.startutc - epoch).total_seconds()
            reqStop  = (sim.stoputc  - epoch).total_seconds()
        else: #ut1_unix
            reqStart = sim.startutc
            reqStop  = sim.stoputc
    except AttributeError: #no specified time
        reqStart = 0. #arbitrary time in the past
        reqStop =  3e9#arbitrary time in the future
#%% determine mutual start/stop frame
# FIXME: assumes that all cameras overlap in time at least a little.
# we will play only over UTC times for which both sites have frames available
    mutualStart = max( [C.filestartutc for C in cam] ) # who started last
    mutualStop =  min( [C.filestoputc  for C in cam] ) # who ended first
#%% make playback time steps
    """
    based on the "simulated" UTC times that do not necessarily correspond exactly
    with either camera.
    """
    tall = arange(mutualStart,mutualStop,sim.kineticsec)

    logging.info('{} mutual frames available from {} to {}'.format(tall.size,
                                  datetime.fromtimestamp(mutualStart,tz=UTC),
                                  datetime.fromtimestamp(mutualStop,tz=UTC)))
#%% adjust start/stop to user request
    treq = tall[(tall>reqStart) & (tall<reqStop)] #keep greater than start time

    logging.info('Per user specification, analyzing {} frames from {} to {}'.format(
                                            treq.size,treq[0], treq[-1]) )
#%% use *nearest neighbor* interpolation to find mutual frames to display.
    """ sometimes one camera will have frames repeated, while the other camera
    might skip some frames altogether
    """
    for C in cam:
        ft = interp1d(C.ut1unix,
                      arange(C.ut1unix.size,dtype=int),
                      kind='nearest')
        C.pbInd = ft(treq).astype(int) #these are the indices for each time (the slower camera will use some frames twice in a row)

    sim.nTimeSlice = treq.size

    return cam,sim

def HSTframeHandler(sim,cam,makeplot,progms,verbose=0):
#%% load 1D cut coord
    cam = get1Dcut(cam,makeplot,progms,verbose)
#%% use 1D cut coord
    logging.info('frameHandler: Loading and 1-D cutting data...')
    tic = time()
    rawdata = []
    for C in cam:
        #40 time faster to read at once, even with this indexing trick than frame by frame
        ind = unique(C.pbInd)
        # http://docs.h5py.org/en/latest/high/dataset.html#fancy-indexing
        # IOError: Can't read data (Src and dest data spaces have different sizes)
        # if you have repeated index in fancy indexing
        with h5py.File(str(C.fn),'r',libver='latest') as f:
            I = f['/rawimg'][ind,...]
            I = I[C.pbInd-ind[0],...] #allows repeated indexes which h5py 2.5 does not for mmap
            I = C.doorientimage(I)
            rawdata.append(I)
#%% assign slice & time to class variables
            C.tKeo = f['/ut1_unix'].value[C.pbInd] #need value for non-Boolean indexing (as of h5py 2.5)

            try: #C.cutrow, C.cutcol only exist if running from histfeas program, not used otherwise
                C.keo = I[:,C.cutrow,C.cutcol].T # row = pix, col = time
            except AttributeError as e:
                logging.debug('skipped extracting 1-D cut {}'.format(e))

    logging.debug('done extracting frames in {:.2f} seconds.'.format(time() - tic))

    return cam,rawdata
