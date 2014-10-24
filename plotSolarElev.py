#!/usr/bin/env python3
'''
tested in Python 3.4 and Python 2.7
Michael Hirsch
 Aug 2012
'''
import ephem  #pip install ephem
import datetime
import matplotlib.pyplot as plt
from numpy import degrees,empty_like,empty
from dateutil.relativedelta import relativedelta

def main(site,coord,year):

    if site:
        # one weird trick
        SiteNames = {
        "Sondrestrom": Sondrestrom,
        "PFISR": PFISR,
        "BU": BU,
        "Svalbard": Svalbard}
        lat, lon, elv = SiteNames.get(site)()
    elif coord is not None:
        lat,lon,elv = coord[0],coord[1],coord[2]


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

    sunaltdate=empty((24*4+1,len(d)),dtype=float)
    for j,dd in enumerate(d):
        t1 = t0 + relativedelta(days=1)
        t = date_range(t0, t1,15,'minutes')

        sunalt = empty_like(t)
        for i,tt in enumerate(t):
            #print(tt)
            obs.date = tt
            sun.compute(obs)

            sunalt[i] = degrees(sun.alt)

        sunaltdate[:,j] = sunalt
        t0 = t1
#%%
#    plt.figure(1); plt.clf()
#    plt.plot(t,sunalt)
#    plt.ylabel('Solar elevation [deg.]')
#    plt.xlabel('UTC')
#    plt.grid(1)
#    plt.title(site + ' ' + t0.strftime(dfmt))

    fg = plt.figure(2,figsize=(12,7),dpi=110)
    ax = fg.gca()
    #plt.imshow(sunaltdate,extent=[0,365,0,23],aspect='auto')#extent=[d0,d1,t0,t1 ]) #contour is better
    V = (-18,-12,-6,-3,0,10,20,30,40,50,60,70,80,90)
    CS = ax.contour(d,t,sunaltdate,V)
    ax.clabel(CS, inline=1, fontsize=10,fmt='%0.0f')#, manual=manual_locations)
    #plt.xlabel('DOY')
    ax.set_ylabel('UTC')
    ax.set_title(site +': ' + str(lat) + ', ' + str(lon) )
    ax.grid(True)
    fg.autofmt_xdate()
    #plt.colorbar()

    plt.show()

'''
http://stackoverflow.com/questions/10688006/generate-a-list-of-datetimes-between-an-interval-in-python
consider using pandas instead
'''
def date_range(start_date, end_date, increment, period):
    result = []
    nxt = start_date
    delta = relativedelta(**{period:increment})
    while nxt <= end_date:
        result.append(nxt)
        nxt += delta
    return result

class Site:
    def __init__(self,lat,lon,elv):
        #we're going to let pyephem do error checking
        self.lat=lat
        self.lon=lon
        self.elv=elv
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

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='plots solar elevation angle')
    p.add_argument('-s','--site',help='use a prestored site [sondrestrom, pfisr, bu, svalbard]',type=str,default='')
    p.add_argument('-c','--coord',help='specify site lat lon [degrees] alt [meters]',
                   nargs=3,type=float,default=[None, None, None])
    p.add_argument('-y','--year',help='year to plot',type=int,default=2014)
    ar = p.parse_args()
    main(ar.site,ar.coord,ar.year)
