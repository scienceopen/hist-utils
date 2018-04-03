import numpy as np
import logging
#
import pymap3d.haversine as haver

def findClosestAzel(az,el,azpts,elpts):
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

    az = np.radians(az)
    el = np.radians(el)
    azpts = np.radians(azpts)
    elpts = np.radians(elpts)

    # can be FAR FAR faster than scipy.spatial.distance.cdist()
    if azpts.ndim==2:
        nearRow = []; nearCol=[]
        for azpt,elpt in zip(azpts,elpts): #list of arrays or 2-D array
            if np.isnan(azpt).all() or np.isnan(elpt).all() and isinstance(azpts,list):
                logging.warning('all points for smaller FOV were outside larger FOV')
                continue

            r,c = _findindex(az,el, azpt,elpt)

            nearRow.append(r)
            nearCol.append(c)
    elif azpts.ndim==1:
        nearRow, nearCol = _findindex(az,el, azpts, elpts)
    else:
        raise ValueError('I only understand 1-D and 2-D FOV overlap requests.')

    return nearRow,nearCol


def _findindex(az,el,azpt,elpt):
    """ point by point """

    assert azpt.size==elpt.size
    r = np.empty(azpt.size,dtype=int)
    c = np.empty(azpt.size,dtype=int)

    for i,(paz,pel) in enumerate(zip(azpt,elpt)):
        #we do this point by point because we need to know the closest pixel for each point
        #errang = haver.anglesep(az,el, apt,ept, deg=False)
        errang = haver.anglesep_meeus(az,el, paz,pel, deg=False)

        """
        THIS UNRAVEL_INDEX MUST BE ORDER = 'C'
        """
        r[i], c[i] = np.unravel_index(errang.argmin(), az.shape,order='C')

    mask = (c==0) | (c == az.shape[1]-1) | (r==0) | (r == az.shape[0]-1)

    r = np.ma.array(r,mask=mask)
    c = np.ma.array(c,mask=mask)

    return r,c
