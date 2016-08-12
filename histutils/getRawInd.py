#!/usr/bin/env python
"""
gets headers from raw .DMCdata binary file
TRAVIS CI: this file is covered by rawDMCreader.py selftest
"""
import logging
from numpy import fromfile,uint16
from struct import pack,unpack

def getRawInd(fn,BytesPerImage,nHeadBytes,Nmetadata):
    assert isinstance(Nmetadata,int)
    if Nmetadata<1: #no header, only raw images
        fileSizeBytes = fn.stat().st_size
        if fileSizeBytes % BytesPerImage:
            logging.error('{} may not be read correctly, mismatch frame->file size'.format(fn))

        firstRawIndex = 1 #definition, one-based indexing
        lastRawIndex = fileSizeBytes // BytesPerImage
    else: # normal case 2013-2016
        # gets first and last raw indices from a big .DMCdata file
        with open(str(fn),'rb') as f: #NOTE didn't use path here due to Python 2.7, Numpy 1.11 lack of pathlib support. Py3.5 is OK
            f.seek(BytesPerImage, 0) # get first raw frame index
            firstRawIndex = meta2rawInd(f,Nmetadata)

            f.seek(-nHeadBytes, 2) #get last raw frame index
            lastRawIndex = meta2rawInd(f,Nmetadata)

    return firstRawIndex, lastRawIndex


def meta2rawInd(f,Nmetadata):
    assert isinstance(Nmetadata,int)

    if Nmetadata<1:
        rawind = None # undefined
    else:
        #FIXME works for .DMCdata version 1 only
        metad = fromfile(f, dtype=uint16, count=Nmetadata)
        metad = pack('<2H',metad[1],metad[0]) # reorder 2 uint16
        rawind = unpack('<I',metad)[0] #always a tuple

    return rawind
