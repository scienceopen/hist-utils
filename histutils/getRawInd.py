"""
gets headers from raw .DMCdata binary file
Michael Hirsch
GPL v3+ license

TRAVIS CI: this file is covered by rawDMCreader.py selftest
"""
from numpy import fromfile,uint16
from struct import pack,unpack

def getRawInd(BigFN,BytesPerImage,nHeadBytes,Nmetadata):
    # gets first and last raw indices from a big .DMCdata file
    with open(str(BigFN),'rb') as f: #NOTE didn't use path here due to Python 2.7, Numpy 1.11 lack of pathlib support. Py3.5 is OK
        f.seek(BytesPerImage, 0) # get first raw frame index
        firstRawIndex = meta2rawInd(f,Nmetadata)

        f.seek(-nHeadBytes, 2) #get last raw frame index
        lastRawIndex = meta2rawInd(f,Nmetadata)

    return firstRawIndex, lastRawIndex


def meta2rawInd(f,Nmetadata):
    #FIXME works for .DMCdata version 1 only
    metad = fromfile(f, dtype=uint16, count=Nmetadata)
    metad = pack('<2H',metad[1],metad[0]) # reorder 2 uint16
    return unpack('<I',metad)[0] #always a tuple
