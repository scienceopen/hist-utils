#!/usr/bin/env python3
"""
Michael Hirsch
following http://www.pveducation.org/pvcdrom/properties-of-sunlight/air-mass
assumes observer at sea level, altitude h \approx 0
"""
from numpy import sin,radians,arange
from matplotlib.pyplot import figure,show

thetaE = arange(90+1,dtype=float)  #solar elevation angle above horizon

M = ( sin(radians(thetaE)) + 0.50572*(6.07995+thetaE)**(-1.6364) )**-1 #air mass factor

ax=figure().gca()
ax.plot(thetaE,M)
ax.set_xlabel('Solar Elevation Angle  [deg.]')
ax.set_ylabel('Air Mass Factor')
ax.set_title('Air Mass Factor vs. elevation angle')
ax.grid(True)

I0 = 1353 # [W]

I = I0 * 0.7**M**0.678

ax=figure().gca()
ax.plot(thetaE,I)
ax.set_title('Solar Irradiance at sea level vs. Solar Elevation Angle')
ax.set_xlabel('Solar Elevation Angle  [deg.]')
ax.set_ylabel('Solar Irradiance at sea level [W m^2]')
ax.grid(True)

show()
