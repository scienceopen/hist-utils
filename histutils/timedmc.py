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
from __future__ import division,absolute_import
from six import string_types
from datetime import datetime
from dateutil.parser import parse
from warnings import warn
from numpy import atleast_1d,int64
from pytz import UTC
from scipy.interpolate import interp1d

#
tepoch = datetime(1970,1,1,0,0,0)

def frame2ut1(tstart,fps,rawind):
    """ if you don't have GPS & fire data, you use this function for a software-only
    estimate of time. This estimate may be off by more than a minute, so think of it
    as a relative indication only. You can try verifying your absolute time with satellite
    passes in the FOV using a plate-scaled calibration and ephemeris data.
    Contact Michael Hirsch, he does have Github code for this.
    """

    if isinstance(tstart,string_types):
        tstart = parse(tstart)
    elif isinstance(tstart,(list,tuple)):
        tstart = tstart[0]
        warn('using first value {} as tstart.'.format(tstart))
        return frame2ut1(tstart,fps,rawind)
    elif isinstance(tstart,datetime):
        pass
    else:
        warn('I do not know how to handle your tstart of type {}'.format(type(tstart)))
        return None

    #total_seconds is required for Python 2 compatibility
    # this variable is in units of seconds since Jan 1, 1970, midnight
    # rawind-1 because camera is one-based indexing
    return (tstart-tepoch).total_seconds() + (rawind-1)/fps

def ut12frame(treq,ind,ut1_unix):
    """
    Given treq, output index(ces) to extract via rawDMCreader
    treq scalar or vector of ut1_unix time (seconds since Jan 1, 1970)
    """
    treq = atleast_1d(treq)

    if not (1e9 < treq[0] < 3e9):
        warn('is your requested date {} valid?'.format(datetime.fromtimestamp(treq[0],tz=UTC)))

#%% get indices
    """
    We use nearest neighbor interpolation to pick a frame index for each requested time
    """
    f = interp1d(ut1_unix,ind,kind='nearest')
    try:
        return f(treq).astype(int64)
    except ValueError:
        warn('a time was requested {} outside the range of times in the data file'.format(datetime.fromtimestamp(treq[0],tz=UTC)))
        return None


def firetime(tstart,Tfire):
    """ Highly accurate sub-millisecond absolute timing based on GPSDO 1PPS and camera fire feedback.
    Right now we have some piecemeal methods to do this, and it's time to make it industrial strength
    code.

    """
    raise NotImplementedError("Yes this is a high priority, would you like to volunteer?")