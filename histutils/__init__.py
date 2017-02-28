from pathlib import Path
from configparser import ConfigParser
from numpy import arange,int64,fromfile,uint16
import logging
from struct import pack,unpack
# NOTE: need to use int64 since Numpy thru 1.11 defaults to int32 for dtype=int, and we need int64 for large files

def getRawInd(fn:Path, BytesPerImage:int, nHeadBytes:int, Nmetadata:int):
    assert isinstance(Nmetadata,int)
    if Nmetadata<1: #no header, only raw images
        fileSizeBytes = fn.stat().st_size
        if fileSizeBytes % BytesPerImage:
            logging.error(f'{fn} may not be read correctly, mismatch frame->file size')

        firstRawIndex = 1 #definition, one-based indexing
        lastRawIndex = fileSizeBytes // BytesPerImage
    else: # normal case 2013-2016
        # gets first and last raw indices from a big .DMCdata file
        with fn.open('rb') as f:
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


def req2frame(req, N:int=0):
    """
    output has to be numpy.arange for > comparison
    """
    if req is None:
        frame = arange(N, dtype=int64)
    elif isinstance(req,int): #the user is specifying a step size
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

def dir2fn(ofn,ifn,suffix) -> Path:
    """
    ofn = filename or output directory, to create filename based on ifn
    ifn = input filename (don't overwrite!)
    suffix = desired file extension e.g. .h5
    """
    if not ofn: # no output file desired
        return

    ofn = Path(ofn).expanduser()
    ifn = Path(ifn).expanduser()
    assert ifn.is_file()

    if ofn.suffix==suffix: #must already be a filename
        pass
    else: #must be a directory
        assert ofn.is_dir(),f'create directory {ofn}'
        ofn = ofn / ifn.with_suffix(suffix).name

    try:
        assert not ofn.samefile(ifn),' do not overwrite input file! {}'.format(ifn)
    except FileNotFoundError: # a good thing, the output file doesn't exist and hence it's not the input file
        pass

    return ofn

def splitconf(conf,key,i=None,dtype=float,fallback=None,sep=','):
    if conf is None:
        return fallback

    #if isinstance(conf, (ConfigParser,SectionProxy)):
   #     pass
    if isinstance(conf,dict):
        try:
            return conf[key][i]
        except TypeError:
            return conf[key]
        except KeyError:
            return fallback
    else:
        pass
        #raise TypeError('expecting dict or configparser')


    if i is not None:
        assert isinstance(i,(int,slice)),'single integer index only'

    if isinstance(key,(tuple,list)):
        if len(key)>1: #drilldown
            return splitconf(conf[key[0]],key[1:],i,dtype,fallback,sep)
        else:
            return splitconf(conf,key[0],i,dtype,fallback,sep)
    elif isinstance(key,str):
        val = conf.get(key,fallback=fallback)
    else:
        raise TypeError(f'invalid key type {type(key)}')

    try:
        return dtype(val.split(sep)[i])
    except (ValueError,AttributeError,IndexError):
        return fallback
    except TypeError:
        if i is None:
            try:
                return [dtype(v) for v in val.split(sep)] #return list of all values instead of just one
            except ValueError:
                return fallback
        else:
            return fallback
