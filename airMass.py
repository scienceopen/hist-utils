#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Michael Hirsch

following http://www.pveducation.org/pvcdrom/properties-of-sunlight/air-mass
assumes observer at sea level, altitude h \approx 0
input: theta [deg] solar elevation angle above horizon
"""
from __future__ import division
from numpy import sin,radians,arange,nan
from matplotlib.pyplot import figure,show

def airmass(thetadeg):
    thetadeg[thetadeg<0] = nan
    thetadeg[thetadeg>90] = nan
    thr = radians(thetadeg)
    """
    Kasten, F., and A. T. Young. 1989. Revised optical air mass tables and approximation formula.
    Applied Optics 28:4735–4738. doi: 10.1364/AO.28.004735
    """
    #Mky = 1/(sin(thr) + 0.50572*(6.07995+thetadeg)**-1.6364) #air mass factor
    """ Young, A. T. 1994. Air mass and refraction. Applied Optics. 33:1108–1110. doi: 10.1364/AO.33.001108. Bibcode 1994ApOpt..33.1108Y. """
    My = ((1.002432*sin(thr)**2 + 0.148386*sin(thr) + 0.0096467) /
          (sin(thr)**3 + 0.149864*sin(thr)**2 + 0.0102963*sin(thr) + 0.000303978))

    I0 = 1353. # [W]

    return I0 * 0.7**My**0.678, My

if __name__ =='__main__':
    theta = arange(90+1,dtype=float)
    Irr,M = airmass(theta)

    ax=figure().gca()
    ax.plot(theta,Irr)
    ax.set_title('Solar Irradiance at sea level vs. Solar Elevation Angle')
    ax.set_xlabel('Solar Elevation Angle  [deg.]')
    ax.set_ylabel('Solar Irradiance at sea level [W m$^2$]')
    ax.grid(True)

    ax=figure().gca()
    ax.plot(theta,M)
    ax.set_xlabel('Solar Elevation Angle  [deg.]')
    ax.set_ylabel('Air Mass Factor')
    ax.set_title('Air Mass Factor vs. elevation angle')
    ax.grid(True)

    show()
