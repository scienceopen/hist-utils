#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tested in Python 3.4 and Python 2.7
Michael Hirsch
 Aug 2012
"""
import ephem  #pip install ephem
import pandas as pd
from matplotlib.pyplot import figure,show
from numpy import degrees,empty_like,empty
from dateutil.relativedelta import relativedelta
#
from airMass import airmass

def main(site,coord,year):

    if site: # one weird trick
        SiteNames = {
        "Sondrestrom": Sondrestrom,
        "PFISR": PFISR,
        "BU": BU,
        "Svalbard": Svalbard}
        lat, lon, elv = SiteNames.get(site)()
    elif coord[0] is not None:
        lat,lon,elv = coord[0],coord[1],coord[2]
    else:
        exit('you must specifiy a site or coordinates')

    obs=ephem.Observer()
    obs.pressure = 1010 # millibar FLOAT
    obs.temp = 15 # deg. Celcius FLOAT
    #obs.horizon = '0' #HAS TO BE A STRING!
    obs.lat = str(lat) #STRING
    obs.lon= str(lon) #STRING
    obs.elevation = float(elv) # meters

    sun = ephem.Sun()

    dates = pd.date_range(start=year+'-01-01', end=year+'-12-31', freq='D')

    sunaltdate,t = elofday(dates,obs,sun)
    plotyear(dates,t,sunaltdate,site,lat,lon)

    Irr = airmass(sunaltdate)[0]
    plotIrr(dates,t,Irr,site,lat,lon)

    show()

def elofday(dates,obs,sun):
    """ compute solar elevation for each day of year"""
    ploteachmin = 15
    sunaltdate=empty((24*60/ploteachmin+1,dates.size),dtype=float)
    t0 = dates[0]
    for j,d in enumerate(dates):
        t1 = t0 + relativedelta(days=1)
        times = pd.date_range(start=t0, end=t1, freq=str(ploteachmin)+'T') #T is minute
        sunaltdate[:,j] = elminutes(times,obs,sun)
        t0 = t1
    return sunaltdate,times

def elminutes(times,obs,sun):
    sunalt = empty_like(times,dtype=float) #need dtype here
    for i,t in enumerate(times):
        obs.date = t
        sun.compute(obs)
        sunalt[i] = sun.alt
    return degrees(sunalt)

def plotyear(dates,t,sunaltdate,site,lat,lon):
    fg = figure(figsize=(12,7),dpi=110)
    ax = fg.gca()
    V = (-18,-12,-6,-3,0,10,20,30,40,50,60,70,80,90)
    CS = ax.contour(dates,t,sunaltdate,V)
    ax.clabel(CS, inline=1, fontsize=10,fmt='%0.0f')#, manual=manual_locations)
    ax.set_ylabel('UTC')
    ax.set_title(''.join(('Solar elevation angle (deg.)  ',site,': ',lat,', ',lon)))
    ax.grid(True)
    fg.autofmt_xdate()

def plotIrr(dates,t,sunaltdate,site,lat,lon):
    fg = figure(figsize=(12,7),dpi=110)
    ax = fg.gca()
    CS = ax.contour(dates,t,sunaltdate)
    ax.clabel(CS, inline=1, fontsize=10,fmt='%0.0f')#, manual=manual_locations)
    ax.set_ylabel('UTC')
    ax.set_title(''.join(('Sea level solar irradiance [W/m$^2$] at ',site,': ',lat,', ',lon)))
    ax.grid(True)
    fg.autofmt_xdate()
    show()

def plotday(t,sunalt,site):
    ax = figure().gca()
    ax.plot(t,sunalt)
    ax.set_ylabel('Solar elevation [deg.]')
    ax.set_xlabel('UTC')
    ax.grid(True)
    ax.set_title(site + ' ' + t[0].strftime('%Y-%m-%d'))

class Site:
    def __init__(self,lat,lon,elv):
        #we're going to let pyephem do error checking
        self.lat=lat
        self.lon=lon
        self.elv=elv
def Sondrestrom():
    return '66.98','-50.94', 180
def PFISR():
    return '65.12', '-147.49', 210
def BU():
    return '42.4', '-71.1', 5
def Svalbard():
    return '78.23', '15.4', 450

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='plots solar elevation angle')
    p.add_argument('-s','--site',help='use a prestored site [sondrestrom, pfisr, bu, svalbard]',type=str,default='')
    p.add_argument('-c','--coord',help='specify site lat lon [degrees] alt [meters]',
                   nargs=3,type=str,default=[None, None, None])
    p.add_argument('-y','--year',help='year to plot',type=str,default='2015')
    ar = p.parse_args()
    main(ar.site,ar.coord,ar.year)
