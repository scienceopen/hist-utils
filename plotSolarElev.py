#!/usr/bin/env python3
"""
tested in Python 3.4 and Python 2.7
Michael Hirsch
 Aug 2012
"""
import astropy.units as u
from astropy.time import Time, TimeDelta
from astropy.coordinates import get_sun, EarthLocation, AltAz
from matplotlib.pyplot import figure,show
from numpy import arange
#
from airMass import airmass

def main(site,coord,year,plotperhour,doplot):
    site = site.lower()
    if len(site) == 0 and coord[0] is not None:
        obs = EarthLocation(lat=coord[0]*u.deg, lon=coord[1]*u.deg, height=coord[2]*u.m)
    elif site == "sondrestrom":
        obs.lat='66.98';obs.lon='-50.94';obs.elevation=180
    elif site=="pfisr":
        obs.lat='65.12';obs.lon='-147.49';obs.elevation=210
    elif site=="bu":
        obs.lat='42.4'; obs.lon='-71.1';obs.elevation=5
    elif site=="svalbard":
        obs.lat='78.23'; obs.lon='15.4';obs.elevation=450
    else:
        exit('*** you must specify a site or coordinates')

    plotperday = 24*plotperhour
    dt = TimeDelta(3600/plotperhour, format='sec')
    times = Time(year+'-01-01T00:00:00',format='isot',scale='utc') + dt * range(365*plotperday)
    dates = times[::plotperday].datetime
    hoursofday = times[:plotperday].datetime

    #yes, we need to feed times to observer and sun!
    sun = get_sun(times).transform_to(AltAz(obstime=times,location=obs))
    sunel = sun.alt.degree.reshape((plotperday,-1),order='F')

    Irr = airmass(sunel)[0]

    if doplot:
        plotIrr(dates,hoursofday,Irr,site,obs)
        plotyear(dates,hoursofday,sunel,site,obs)

        show()

    return Irr,sunel

def plotyear(dates,hoursofday,sunel,site,obs):
    fg = figure(figsize=(12,7),dpi=110)
    ax = fg.gca()
    V = (-18,-12,-6,-3,0,10,20,30,40,50,60,70,80,90)
    CS = ax.contour(dates,hoursofday,sunel,V)
    ax.clabel(CS, inline=1, fontsize=10,fmt='%0.0f')#, manual=manual_locations)
    ax.set_ylabel('UTC')
    ax.set_title(''.join(('Solar elevation angle (deg.)  ',site,': ',
                          str(obs.latitude),', ',str(obs.longitude))))
    ax.grid(True)
    fg.autofmt_xdate()

def plotIrr(dates,hoursofday,sunel,site,obs):
    fg = figure(figsize=(12,7),dpi=110)
    ax = fg.gca()
    CS = ax.contour(dates,hoursofday,sunel)
    ax.clabel(CS, inline=1, fontsize=10,fmt='%0.0f')#, manual=manual_locations)
    ax.set_ylabel('UTC')
    ax.set_title(''.join(('Sea level solar irradiance [W/m$^2$] at ',site,': ',
                          str(obs.latitude),', ',str(obs.longitude))))
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

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='plots solar elevation angle')
    p.add_argument('-s','--site',help='use a prestored site [sondrestrom, pfisr, bu, svalbard]',type=str,default='')
    p.add_argument('-c','--coord',help='specify site lat lon [degrees] ',
                   nargs=3,type=float,default=(None, None, None))
    p.add_argument('-y','--year',help='year to plot',type=str,default='2015')
    p.add_argument('--pph',help='plot steps per hour (default 1)',type=int,default=1)
    p.add_argument('--noplot',help='disable plotting',action='store_false')
    ar = p.parse_args()
    Irr, sunel = main(ar.site,ar.coord,ar.year,ar.pph,ar.noplot)
