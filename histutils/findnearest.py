from numpy import unravel_index,ma,atleast_1d,empty
#
from pymap3d.haversine import angledist

def findClosestAzel(az,el,azpts,elpts,discardEdgepix=True):
    """
    assumes that azpts, elpts are each list of 1-D arrays or 2-D arrays
    az: 2-D Numpy array of azimuths in the image
    el: 2-D Numpy array of elevations in the image
    azpts: 1-D or 2-D Numpy array of azimuth points to see where nearest neighbor index is
    elpts: 1-D or 2-D Numpy array of azimuth points to see where nearest neighbor index is
    """
    assert az.ndim     == 2
    assert az.shape    == el.shape
    assert azpts.shape == elpts.shape

    az = ma.masked_invalid(az)
    el = ma.masked_invalid(el)
    nearRow = []; nearCol=[]
    # can be FAR FAR faster than scipy.spatial.distance.cdist()
    for apts,epts in zip(azpts,elpts): #list of arrays or 2-D array
        apts = atleast_1d(apts); epts = atleast_1d(epts) # needed
        assert apts.size==epts.size
        r = empty(apts.size,dtype=int); c = empty(apts.size,dtype=int)
        for i,(apt,ept) in enumerate(zip(apts,epts)):
            #we do this point by point because we need to know the closest pixel for each point
            errang = angledist(az,el, apt,ept)

            """
            THIS UNRAVEL_INDEX MUST BE ORDER = 'C'
            """
            r[i], c[i] = unravel_index(errang.argmin(), az.shape,order='C')

        if discardEdgepix:
            mask = ((c==0) | (c == az.shape[1]-1) |
                    (r==0) | (r == az.shape[0]-1))
        else:
            mask = False

        nearRow.append(ma.array(r,mask=mask))
        nearCol.append(ma.array(c,mask=mask))

    return nearRow,nearCol
