#!/usr/bin/env python3
# Michael Hirsch
# following http://www.pveducation.org/pvcdrom/properties-of-sunlight/air-mass
import numpy as np
import matplotlib.pyplot as plt

thetaE = np.arange(91,dtype=float)  #solar elevation angle above horizon

M = ( np.sin(np.radians(thetaE)) + 0.50572*(6.07995+thetaE)**(-1.6364) )**-1 #air mass factor

plt.figure(1)
plt.plot(thetaE,M)
plt.xlabel('Solar Elevation Angle  [deg.]')
plt.ylabel('Air Mass Factor')
plt.title('Air Mass Factor vs. elevation angle')
plt.grid(True)

I0 = 1353 # [W]

I = I0 * 0.7**M**0.678

plt.figure(2)
plt.plot(thetaE,I)
plt.title('Solar Irradiance at ground level vs. Elevation Angle')
plt.xlabel('Solar Elevation Angle  [deg.]')
plt.ylabel('Solar Irradiance at ground level [W m^2]')
plt.grid(True)