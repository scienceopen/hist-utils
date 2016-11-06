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
from numpy import (empty_like,absolute,atleast_1d,asanyarray,empty,
                   unravel_index,ma,nanargmin)
#from bisect import bisect
#
from pymap3d.haversine import angledist

def find_nearest(x,x0):
    x = asanyarray(x) #for indexing upon return
    x0 = atleast_1d(x0)
    if x.size==0 or x0.size==0:
        logging.error('empty input(s)')
        return None, None

    ind = empty_like(x0,dtype=int)

    # NOTE: not trapping IndexError (all-nan) becaues returning None can surprise with slice indexing
    for i,xi in enumerate(x0):
        ind[i] = nanargmin(absolute(x-xi))

    return ind.squeeze()[()], x[ind].squeeze()[()]   # [()] to pop scalar from 0d array while being OK with ndim>0

def findClosestAzel(az,el,azpts,elpts,discardEdgepix=True):
    """
    assumes that azpts, elpts are each list of 1-D arrays or 2-D arrays

    """
    assert az.ndim     == 2
    assert az.shape    == el.shape
    assert azpts.shape == elpts.shape

    az = ma.masked_invalid(az)
    el = ma.masked_invalid(el)
    nearRow = []; nearCol=[]
    # can be FAR FAR faster than scipy.spatial.distance.cdist()
    for apts,epts in zip(azpts,elpts): #list of arrays or 2-D array
        assert apts.size==epts.size
        r = empty(apts.size,dtype=int); c = empty(apts.size,dtype=int)
        for i,(apt,ept) in enumerate(zip(apts,epts)):
            #we do this point by point because we need to know the closest pixel for each point
            errang = angledist(az,el, apt,ept)

    # ********************************************
    # THIS UNRAVEL_INDEX MUST BE ORDER = 'C'
            r[i], c[i] = unravel_index(errang.argmin(), az.shape,order='C')
    #************************************************



        if discardEdgepix:
            mask = ((c==0) | (c == az.shape[1]-1) |
                    (r==0) | (r == az.shape[0]-1))
        else:
            mask = False

        nearRow.append(ma.array(r,mask=mask))
        nearCol.append(ma.array(c,mask=mask))

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
