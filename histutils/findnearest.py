import numpy as np
import logging
#
import pymap3d.haversine as haver

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

    az = np.ma.masked_invalid(az)
    el = np.ma.masked_invalid(el)
    nearRow = []; nearCol=[]

    az = np.radians(az)
    el = np.radians(el)
    azpts = np.radians(azpts)
    elpts = np.radians(elpts)

    # can be FAR FAR faster than scipy.spatial.distance.cdist()
    for apts,epts in zip(azpts,elpts): #list of arrays or 2-D array
        apts = np.atleast_1d(apts)
        epts = np.atleast_1d(epts) # needed
        if np.isnan(apts).all() or np.isnan(epts).all() and isinstance(azpts,list):
            logging.warning('all points for smaller FOV were outside larger FOV')
            continue
        assert apts.size==epts.size
        r = np.empty(apts.size,dtype=int)
        c = np.empty(apts.size,dtype=int)
        for i,(apt,ept) in enumerate(zip(apts,epts)):
            #we do this point by point because we need to know the closest pixel for each point
            #errang = haver.anglesep(az,el, apt,ept, deg=False)
            errang = haver.anglesep_meeus(az,el, apt,ept, deg=False)

            """
            THIS UNRAVEL_INDEX MUST BE ORDER = 'C'
            """
            r[i], c[i] = np.unravel_index(errang.argmin(), az.shape,order='C')

        if discardEdgepix:
            mask = ((c==0) | (c == az.shape[1]-1) |
                    (r==0) | (r == az.shape[0]-1))
        else:
            mask = False

        nearRow.append(np.ma.array(r,mask=mask))
        nearCol.append(np.ma.array(c,mask=mask))

    return nearRow,nearCol
