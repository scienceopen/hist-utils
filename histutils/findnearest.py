"""
This find_nearest function does NOT assume sorted input

inputs:
x: array (float, int, datetime) within which to search for x0
x0: singleton or array of values to search for in x

outputs:
idx: index of flattened x nearest to x0  (i.e. works with higher than 1-D arrays also)
xidx: x[idx]

Observe how bisect.bisect() gives the incorrect result!

idea based on http://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array

Michael Hirsch
GPLv3+
"""
from __future__ import division,absolute_import
import logging
from numpy import (empty_like,absolute,atleast_1d,asanyarray,empty,hypot,
                   delete,unravel_index,logical_not)
#from bisect import bisect

def find_nearest(x,x0):
    x = asanyarray(x) #for indexing upon return
    x0 = atleast_1d(x0)
    if x.size==0 or x0.size==0:
        logging.error('empty input(s)')
        return None, None

    ind = empty_like(x0,dtype=int)

    for i,xi in enumerate(x0):
        ind[i] = absolute(x-xi).argmin()

    return ind.squeeze(), x[ind].squeeze()

def findClosestAzel(az,el,azpts,elpts,discardEdgepix=True):
    assert az.shape    == el.shape
    assert azpts.shape == elpts.shape
    assert az.ndim == 2

    npts = azpts.size  #numel
    nearRow = empty(npts,dtype=int)
    nearCol = empty(npts,dtype=int)
    # can be FAR FAR faster than scipy.spatial.distance.cdist()
    for i in range(npts):
        #we do this point by point because we need to know the closest pixel for each point
        errdist = absolute( hypot(az - azpts[i],
                                  el - elpts[i]) )

# ********************************************
# THIS UNRAVEL_INDEX MUST BE ORDER = 'C'
        nearRow[i],nearCol[i] = unravel_index(errdist.argmin(),
                                              az.shape,order='C')
#************************************************


    if discardEdgepix:
        mask = logical_not(((nearCol==0) | (nearCol == az.shape[1]-1)) |
                           ((nearRow==0) | (nearRow == az.shape[0]-1)))
        nearRow = nearRow[mask]
        nearCol = nearCol[mask]

    return nearRow,nearCol

#def INCORRECTRESULT_using_bisect(x,X0): #pragma: no cover
#    X0 = atleast_1d(X0)
#    x.sort()
#    ind = [bisect(x,x0) for x0 in X0]
#
#    x = asanyarray(x)
#    return asanyarray(ind),x[ind]

#if __name__ == '__main__':

    #print(find_nearest([10,15,12,20,14,33],[32,12.01]))

    #print(INCORRECTRESULT_using_bisect([10,15,12,20,14,33],[32,12.01]))
