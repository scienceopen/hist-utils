from __future__ import division,absolute_import
#
from .normframe import normframe
"""
Note: consider using scipy.misc.bytescale instead of this file.

inputs:
-------
I: 2-D Numpy array of grayscale image data
Clim: length 2 of tuple or numpy 1-D array specifying lowest and highest expected values in grayscale image
Michael Hirsch
"""

def sixteen2eight(I,Clim):
    Q = normframe(I,Clim)
    Q *= 255 # stretch to [0,255] as a float
    return Q.round().astype('uint8') # convert to uint8
