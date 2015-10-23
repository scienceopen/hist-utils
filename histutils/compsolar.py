from numpy import trapz,isnan
import astropy.units as u
from astropy.coordinates import get_sun, EarthLocation, AltAz
from astropy.time import Time
from datetime import datetime
from warnings import warn
from dateutil.rrule import HOURLY,rrule
from matplotlib.dates import MonthLocator,DateFormatter
from matplotlib.pyplot import figure
try:
    import seaborn as sns
    sns.color_palette(sns.color_palette("cubehelix"))
    sns.set(context='poster', style='whitegrid')
    sns.set(rc={'image.cmap': 'cubehelix_r'}) #for contour
except:
    pass
#
from .airMass import airmass

def compsolar(site,coord,year,plotperhour,doplot):
    if isinstance(year,datetime):
        year=year.year
#%%
    site = site.lower()
    if len(site) == 0 and coord[0] is not None:
        obs = EarthLocation(lat=coord[0]*u.deg, lon=coord[1]*u.deg, height=coord[2]*u.m)
    elif site == "sondrestrom":
        obs = EarthLocation(lat=66.98*u.deg, lon=-50.94*u.deg, height=180*u.m)
    elif site=="pfisr":
        obs = EarthLocation(lat=65.12*u.deg, lon=-147.49*u.deg, height=210*u.m)
    elif site=="bu":
        obs = EarthLocation(lat=42.4*u.deg, lon=-71.1*u.deg, height=5*u.m)
    elif site=="svalbard":
        obs = EarthLocation(lat=78.23*u.deg, lon=15.4*u.deg, height=450*u.m)
    else:
        warn('you must specify a site or coordinates')
        return None, None

    plotperday = 24*plotperhour
    #don't fool around with Pandas or Numpy, since Numpy datetime64 doesn't work with Matplotlib
    times = list(rrule(HOURLY,
                       dtstart=datetime(year,1,1,0,0,0),
                       until=datetime(year,12,31,23,59,59)))

    dates = times[::plotperday]
    hoursofday = times[:plotperday]

    #yes, we need to feed times to observer and sun!
    sun = get_sun(Time(times)).transform_to(AltAz(obstime=times,location=obs))
    sunel = sun.alt.degree.reshape((plotperday,-1),order='F')

    Irr = airmass(sunel,times)[0]

    Whr = estenergy(Irr,hoursofday)

    if doplot:
        lbl=MonthLocator(range(1,13),bymonthday=15,interval=1)
        fmt=DateFormatter("%b")
        plotIrr(dates,hoursofday,Irr,site,obs,lbl,fmt)
        plotyear(dates,hoursofday,sunel,site,obs,lbl,fmt)
        plotenergy(Whr,dates,site,obs,lbl,fmt)

    return Irr,sunel,Whr

def estenergy(Irr,hoursofday):
    secs = [(h-hoursofday[0]).total_seconds()/3600 for h in hoursofday]
    Irr[isnan(Irr)] = 0
    return trapz(Irr,x=secs,axis=0)

def plotyear(dates,hoursofday,sunel,site,obs,lbl,fmt):
    fg = figure(figsize=(12,7),dpi=100)
    ax = fg.gca()
    V = (-18,-12,-6,-3,0,10,20,30,40,50,60,70,80,90)
    CS = ax.contour(dates,hoursofday,sunel,V)
    ax.clabel(CS, inline=1, fontsize=10,fmt='%0.0f')#, manual=manual_locations)
    ax.set_ylabel('UTC')
    ax.set_title('Solar elevation angle (deg.)  {}: {:.1f},{:.1f}'.format(site,obs.latitude,obs.longitude))
    ax.grid(True)
#    fg.autofmt_xdate()
    ax.xaxis.set_major_locator(lbl)
    ax.xaxis.set_major_formatter(fmt)

def plotIrr(dates,hoursofday,sunel,site,obs,lbl,fmt):
    fg = figure(figsize=(12,7),dpi=100)
    ax = fg.gca()
    CS = ax.contour(dates,hoursofday,sunel)
    ax.clabel(CS, inline=1, fontsize=10,fmt='%0.0f')#, manual=manual_locations)
    ax.set_ylabel('UTC')
    ax.set_title('Sea level solar irradiance [W/m$^2$] at {}: {:.1f},{:.1f}'.format(site,obs.latitude,obs.longitude))
    ax.grid(True)
#    fg.autofmt_xdate()
    ax.xaxis.set_major_locator(lbl)
    ax.xaxis.set_major_formatter(fmt)

def plotday(t,sunalt,site):
    ax = figure().gca()
    ax.plot(t,sunalt)
    ax.set_ylabel('Solar elevation [deg.]')
    ax.set_xlabel('UTC')
    ax.grid(True)
    ax.set_title(site + ' ' + t[0].strftime('%Y-%m-%d'))

def plotenergy(Whr,dates,site,obs,lbl,fmt):
    ax = figure().gca()
    ax.plot(dates,Whr/1000)
    ax.set_xlabel('UTC')
    ax.set_ylabel('kWhr m$^{-2}$ day$^{-1}$')
    ax.set_title('Daily Solar Energy at {}: {:.1f}, {:.1f}'.format(site,obs.latitude,obs.longitude))
    ax.xaxis.set_major_locator(lbl)
    ax.xaxis.set_major_formatter(fmt)