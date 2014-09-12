# gets headers from raw .DMCdata binary file
# Michael Hirsch
# GPL v3+ license
from numpy import fromfile,uint16
from struct import pack,unpack
from os.path import expanduser

def getRawInd(BigFN,BytesPerImage,nHeadBytes,Nmetadata):
    #handle ~ in filename
    BigFN = expanduser(BigFN)
    # gets first and last raw indices from a big .DMCdata file
    with open(BigFN,'rb') as fid:

        fid.seek( int(BytesPerImage) ,0) # get first raw frame index
        firstRawIndex = meta2rawInd(fid,Nmetadata)

        fid.seek(-nHeadBytes,2) #get last raw frame index
        lastRawIndex = meta2rawInd(fid,Nmetadata)

    return firstRawIndex, lastRawIndex


def meta2rawInd(fid,Nmetadata):
    #TODO works for .DMCdata only, not bigger header files!
    metad = fromfile(fid, dtype=uint16, count=Nmetadata)
    metad = pack('<2H',metad[1],metad[0]) # reorder 2 uint16
    rawInd = unpack('<I',metad)[0] #always a tuple
    return rawInd
