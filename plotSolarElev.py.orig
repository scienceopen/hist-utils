#!/usr/bin/env python3
#tested in Python 3.4.0 and Python 2.7.6
# Michael Hirsch
# Aug 2012
import sys
import ephem  #pip install ephem
import datetime
import matplotlib.pyplot as plt
import numpy as np
from dateutil.relativedelta import relativedelta

def main(argv):
    
    year = 2014

    if len(argv) < 2:
        site = 'PFISR'
    else:
        site = argv[1]

    SiteNames = {
    "Sondrestrom": Sondrestrom,
    "PFISR": PFISR,
    "BU": BU,
    "Svalbard": Svalbard}

    lat, lon, elv = SiteNames.get(site)()


    obs=ephem.Observer()
    obs.pressure = 1010 # millibar FLOAT
    obs.temp = 15 # deg. Celcius FLOAT
    #obs.horizon = '0' #HAS TO BE A STRING!
    obs.lat = lat #STRING
    obs.lon= lon #STRING
    obs.elevation = elv # meters
    

    sun = ephem.Sun()


    #t = np.arange(t0,t0 + np.timedelta64(24,'h') ,dtype='datetime64[h]') #didn't like\
    d0 = datetime.datetime(year,1,1)
    d1 = datetime.datetime(year,12,31)
    d = date_range(d0, d1,1,'days')

    t0 = d0
    
    sunaltdate=np.empty((24*4+1,len(d)),dtype=float)
    for j,dd in enumerate(d):
        t1 = t0 + relativedelta(days=1)
        t = date_range(t0, t1,15,'minutes')

        sunalt = np.empty(len(t))
        for i,tt in enumerate(t):
            #print(tt)
            obs.date = tt
            sun.compute(obs)

            sunalt[i] = np.rad2deg(sun.alt)

        sunaltdate[:,j] = sunalt
        t0 = t1
#%%
#    plt.figure(1); plt.clf()
#    plt.plot(t,sunalt)
#    plt.ylabel('Solar elevation [deg.]')
#    plt.xlabel('UTC')
#    plt.grid(1)
#    plt.title(site + ' ' + t0.strftime(dfmt))

    fig = plt.figure(2,figsize=(12,7),dpi=110); plt.clf()
    #plt.imshow(sunaltdate,extent=[0,365,0,23],aspect='auto')#extent=[d0,d1,t0,t1 ]) #contour is better
    V = (-18,-12,-6,-3,0,10,20,30,40,50,60,70,80,90)
    CS = plt.contour(d,t,sunaltdate,V)
    plt.clabel(CS, inline=1, fontsize=10)#, manual=manual_locations)
    #plt.xlabel('DOY')
    plt.ylabel('UTC')
    plt.title(site +': ' + str(lat) + ', ' + str(lon) )
    plt.grid(True)
    fig.autofmt_xdate()
    #plt.colorbar()

    plt.show()

#http://stackoverflow.com/questions/10688006/generate-a-list-of-datetimes-between-an-interval-in-python
def date_range(start_date, end_date, increment, period):
    result = []
    nxt = start_date
    delta = relativedelta(**{period:increment})
    while nxt <= end_date:
        result.append(nxt)
        nxt += delta
    return result

# hmm, dictionary 
def Sondrestrom():
    lat='66.98'
    lon='-50.94'
    elv=180 # meters
    return lat, lon, elv
def PFISR():
    lat='65.12'
    lon='-147.49'
    elv=210
    return lat, lon, elv
def BU():
    lat='42.4'
    lon='-71.1'
    elv=5
    return lat, lon, elv
def Svalbard():
    lat='78.23'
    lon='15.4'
    elv=450
    return lat, lon, elv



main(sys.argv)
