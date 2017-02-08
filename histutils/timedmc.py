#!/usr/bin/env python3
"""
Estimates time of DMC frames using GPS & fire data, when they exist.
work in progress

We use UT1 Unix epoch time instead of datetime, since we are working with HDF5 and also need to do fast comparisons

Outputs:
--------
    UT1_unix:   double-precision float (64-bit) estimate of frame exposure START

Michael Hirsch
"""
from datetime import datetime
from dateutil.parser import parse
from numpy import atleast_1d,int64,empty,datetime64
from scipy.interpolate import interp1d
#
from sciencedates import forceutc


def frame2ut1(tstart,kineticsec,rawind):
    """ if you don't have GPS & fire data, you use this function for a software-only
    estimate of time. This estimate may be off by more than a minute, so think of it
    as a relative indication only. You can try verifying your absolute time with satellite
    passes in the FOV using a plate-scaled calibration and ephemeris data.
    Contact Michael Hirsch, he does have Github code for this.
    """
    #total_seconds is required for Python 2 compatibility
    # this variable is in units of seconds since Jan 1, 1970, midnight
    # rawind-1 because camera is one-based indexing
    try:
        return datetime2unix(tstart)[0] + (rawind-1)*kineticsec
    except TypeError:
        return

def ut12frame(treq,ind,ut1_unix):
    """
    Given treq, output index(ces) to extract via rawDMCreader
    treq scalar or vector of ut1_unix time (seconds since Jan 1, 1970)
    """
    if treq is None: #have to do this since interp1 will return last index otherwise
        return

    treq = atleast_1d(treq)
#%% handle human specified string scalar case
    if treq.size == 1:
        treq = datetime2unix(treq[0])
#%% handle time range case
    elif treq.size == 2:
        tstartreq = datetime2unix(treq[0])
        tendreq = datetime2unix(treq[1])
        treq = ut1_unix[(ut1_unix>tstartreq) & (ut1_unix<tendreq)]
    else: #otherwise, it's a vector of requested values
        treq = datetime2unix(treq)
#%% get indices
    """
    We use nearest neighbor interpolation to pick a frame index for each requested time.
    """
    f = interp1d(ut1_unix,ind,kind='nearest',bounds_error=True,assume_sorted=True) #it won't output nan for int case in Numpy 1.10 and other versions too
    framereq = f(treq).astype(int64)
    framereq = framereq[framereq>=0] #discard outside time limits
    return framereq


def datetime2unix(T):
    """
    converts datetime to UT1 unix epoch time
    """
    T = atleast_1d(T)

    ut1_unix = empty(T.shape,dtype=float)
    for i,t in enumerate(T):
        if isinstance(t,(datetime,datetime64)):
            pass
        elif isinstance(t,str):
            try:
                ut1_unix[i] = float(t) #it was ut1_unix in a string
                continue
            except ValueError:
                t = parse(t) #datetime in a string
        elif isinstance(t,(float,int)): #assuming ALL are ut1_unix already
            return T
        else:
            raise TypeError('I only accept datetime or parseable date string')

        ut1_unix[i] = forceutc(t).timestamp() #ut1 seconds since unix epoch, need [] for error case

    return ut1_unix


def firetime(tstart,Tfire):
    """ Highly accurate sub-millisecond absolute timing based on GPSDO 1PPS and camera fire feedback.
    Right now we have some piecemeal methods to do this, and it's time to make it industrial strength
    code.

    """
    raise NotImplementedError("Yes this is a high priority, would you like to volunteer?")
