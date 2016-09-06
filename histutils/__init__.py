try:
    from pathlib import Path
    Path().expanduser()
except (ImportError,AttributeError):
    from pathlib2 import Path
#
from . import Path
from six import integer_types
from numpy import arange,int64,fromfile,uint16
import logging
from struct import pack,unpack
# NOTE: need to use int64 since Numpy thru 1.11 defaults to int32 for dtype=int, and we need int64 for large files

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


def req2frame(req, N=0):
    """
    output has to be numpy.arange for > comparison
    """
    if req is None:
        frame = arange(N, dtype=int64)
    elif isinstance(req,integer_types): #the user is specifying a step size
        frame = arange(0, N, req, dtype=int64)
    elif len(req) == 1:
        frame = arange(0, N, req[0], dtype=int64)
    elif len(req) == 2:
        frame = arange(req[0], req[1], dtype=int64)
    elif len(req) == 3:
        # this is -1 because user is specifying one-based index
        frame = arange(req[0], req[1], req[2], dtype=int64) - 1 # keep -1 !
    else: # just return all frames
        frame = arange(N, dtype=int64)

    return frame

def dir2fn(ofn,ifn,suffix):
    """
    ofn = filename or output directory, to create filename based on ifn
    ifn = input filename (don't overwrite!)
    suffix = desired file extension e.g. .h5
    """
    if not ofn: # no output file desired
        return None

    ofn = Path(ofn).expanduser()
    ifn = Path(ifn).expanduser()
    assert ifn.is_file()

    if ofn.suffix==suffix: #must already be a filename
        pass
    else: #must be a directory
        assert ofn.is_dir(),'create directory {}'.format(ofn)
        ofn = ofn / ifn.with_suffix(suffix).name

    try:
        assert not ofn.samefile(ifn),' do not overwrite input file! {}'.format(ifn)
    except FileNotFoundError: # a good thing, the output file doesn't exist and hence it's not the input file
        pass

    return ofn