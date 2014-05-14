# gets headers from raw .DMCdata binary file
# Michael Hirsch
# GPL v3+ license
import numpy as np
import struct
import os

def getRawInd(BigFN,BytesPerImage,nHeadBytes,Nmetadata):
    #handle ~ in filename
    BigFN = os.path.expanduser(BigFN)
    # gets first and last raw indices from a big .DMCdata file
    fid=open(BigFN,'rb')

    fid.seek( int(BytesPerImage) ,0) # get first raw frame index
    firstRawIndex = meta2rawInd(fid,Nmetadata)

    fid.seek(-nHeadBytes,2) #get last raw frame index
    lastRawIndex = meta2rawInd(fid,Nmetadata)

    fid.close()
    return firstRawIndex, lastRawIndex


def meta2rawInd(fid,Nmetadata):
    #TODO works for .DMCdata only, not bigger header files!
    metad = np.fromfile(fid, np.uint16,Nmetadata)
    metad = struct.pack('<2H',metad[1],metad[0]) # reorder 2 uint16
    rawInd = struct.unpack('<I',metad)[0]
    return rawInd
