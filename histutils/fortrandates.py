from __future__ import division,absolute_import
from six import string_types,integer_types
from datetime import timedelta,datetime, time
from pytz import UTC
from numpy import atleast_1d, empty_like, atleast_2d,nan,empty,datetime64
from dateutil.parser import parse

def datetime2yd(T):
    """
    Inputs:
    T: Numpy 1-D array of datetime.datetime OR string suitable for dateutil.parser.parse

    Outputs:
    yd: yyyyddd four digit year, 3 digit day of year (INTEGER)
    utsec: seconds from midnight utc
    """
    T = atleast_1d(T)

    utsec=empty_like(T,dtype=float)
    yd = empty_like(T,dtype=int)
    for i,t in enumerate(T):
        if isinstance(t,string_types):
            t = parse(t)

        assert isinstance(t,datetime)

        t=forceutc(t)
        utsec[i] = dt2utsec(t)
        yd[i] = t.year*1000 + int(t.strftime('%j'))

    return yd,utsec


def datetime2gtd(T,glon=nan):
    """
    Inputs:
    T: Numpy 1-D array of datetime.datetime OR string suitable for dateutil.parser.parse
    glon: Numpy 2-D array of geodetic longitudes (degrees)

    Outputs:
    iyd: day of year
    utsec: seconds from midnight utc
    stl: local solar time
    """
    T = atleast_1d(T); glon=atleast_2d(glon)
    iyd=empty_like(T,dtype=int)
    utsec=empty_like(T,dtype=float)
    stl = empty((T.size,glon.shape[0],glon.shape[1]))

    for i,t in enumerate(T):
        if isinstance(t,string_types):
            t = parse(t)

        assert isinstance(t,datetime)

        t = forceutc(t)
        iyd[i] = int(t.strftime('%j'))
        #seconds since utc midnight
        utsec[i] = dt2utsec(t)

        stl[i,...] = utsec[i]/3600 + glon/15 #FIXME let's be sure this is appropriate
    return iyd,utsec,stl

def dt2utsec(t):
    """ seconds since utc midnight"""
    assert isinstance(t,datetime)

    return timedelta.total_seconds(t-datetime.combine(t.date(),time(0,tzinfo=UTC)))


def forceutc(t):
    """
    Add UTC to datetime-naive and convert to UTC for datetime aware
    
    input: python datetime (naive, utc, non-utc) or Numpy datetime64  #FIXME add Pandas and AstroPy time classes
    output: utc datetime
    """
    if isinstance(t,datetime64):
        t=t.astype('M8[ms]').astype('O') #for Numpy 1.10 at least...
    elif isinstance(t,datetime):
        pass
    else:
        raise TypeError('datetime only input')

    if t.tzinfo == None: #datetime-naive
        t = t.replace(tzinfo = UTC)
    else: #datetime-aware
        t = t.astimezone(UTC) #changes timezone, preserving absolute time. E.g. noon EST = 5PM UTC
    return t


"""
http://stackoverflow.com/questions/19305991/convert-fractional-years-to-a-real-date-in-python
Authored by "unutbu" http://stackoverflow.com/users/190597/unutbu

In Python, go from decimal year (YYYY.YYY) to datetime,
and from datetime to decimal year.
"""
def yeardec2datetime(atime):
    """
    Convert atime (a float) to DT.datetime
    This is the inverse of dt2t.
    assert dt2t(t2dt(atime)) == atime
    """
    assert isinstance(atime,(float,integer_types)) #typically a float

    year = int(atime)
    remainder = atime - year
    boy = datetime(year, 1, 1)
    eoy = datetime(year + 1, 1, 1)
    seconds = remainder * (eoy - boy).total_seconds()
    return boy + timedelta(seconds=seconds)

def datetime2yeardec(t):
    """
    Convert a datetime into a float. The integer part of the float should
    represent the year.
    Order should be preserved. If adate<bdate, then d2t(adate)<d2t(bdate)
    time distances should be preserved: If bdate-adate=ddate-cdate then
    dt2t(bdate)-dt2t(adate) = dt2t(ddate)-dt2t(cdate)
    """
    if isinstance(t,string_types):
        t = parse(t)

    assert isinstance(t,datetime)

    year = t.year
    boy = datetime(year, 1, 1)
    eoy = datetime(year + 1, 1, 1)
    return year + ((t - boy).total_seconds() / ((eoy - boy).total_seconds()))
