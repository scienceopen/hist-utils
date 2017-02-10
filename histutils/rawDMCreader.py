#!/usr/bin/env python
"""
reads .DMCdata files and displays them
 Michael Hirsch
NOTE: Observe the dtype=np.int64, this is for Windows Python, that wants to
   default to int32 instead of int64 like everyone else!
 """
from pathlib import Path
import logging
import re
from dateutil.parser import parse
from numpy import int64,uint16,zeros,arange,fromfile
from re import search
from astropy.io import fits
#
try:
    from shutil import disk_usage
except ImportError: #Python 2
    from psutil import disk_usage
#
from . import req2frame,dir2fn,getRawInd,meta2rawInd
from .h5imgwriter import setupimgh5,imgwriteincr
from .timedmc import frame2ut1,ut12frame
#
try:
    import tifffile
except:
    tifffile=None
#
bpp = 16

def goRead(fn,xyPix,xyBin,FrameIndReq=None, ut1Req=None,kineticraw=None,startUTC=None,cmosinit=None,verbose=0,outfn=None,nHeadBytes=4):

    fn = Path(fn).expanduser()
    ext = fn.suffix
#%% optional output file setup
    outfn = dir2fn(outfn,fn,'.h5')
    if outfn:
        freeout =  disk_usage(str(outfn.parent)).free
        if freeout < 10e9 or freeout < 10*fn.stat().st_size:
            raise RuntimeError('out of disk space on {}'.format(outfn.parent))
#%% setup data parameters
    if ext in ('.DMCdata','.dat'):
        # preallocate *** LABVIEW USES ROW-MAJOR ORDERING C ORDER
        finf = getDMCparam(fn,xyPix,xyBin,FrameIndReq,ut1Req,kineticraw,startUTC,nHeadBytes,verbose)
        rawFrameInd = zeros(finf['nframeextract'], dtype=int64)
#%% output (variable or file)
        if outfn:
            setupimgh5(outfn,finf['nframeextract'],finf['supery'],finf['superx'])
            data = None
        else:
            data = zeros((finf['nframeextract'],finf['supery'],finf['superx']),
                    dtype=uint16, order='C')
#%% read
        with fn.open('rb') as fid: #NOTE: not pathlib due to Python 2.7, Numpy 1.11 incompat. Py3.5 OK
            for j,i in enumerate(finf['frameindrel']): #j and i are NOT the same in general when not starting from beginning of file!
                D, rawFrameInd[j] = getDMCframe(fid,i,finf,verbose)
                if outfn:
                    imgwriteincr(outfn,D,j)
                else:
                    data[j,...] = D
#%% absolute time estimate, software timing (at your peril)
        finf['ut1'] = frame2ut1(startUTC,kineticraw,rawFrameInd)


    elif ext[:4] == '.tif':
        finf,data = getNeoParam(fn,FrameIndReq,ut1Req,kineticraw,startUTC,cmosinit,verbose)
        rawFrameInd = finf['frameind'] #FIXME this is for individual file, not start of night.
    else:
        raise ValueError('not sure to do with file {}'.format(fn))

    return data, rawFrameInd,finf#,ut1_unix
#%% workers
def getserialnum(flist):
    """
    This function assumes the serial number of the camera is in a particular place in the filename.
    Yes, this is a little lame, but it's how the original 2011 image-writing program worked, and I've
    carried over the scheme rather than appending bits to dozens of TB of files.
    """
    sn = []
    for f in flist:
        tmp = search(r'(?<=CamSer)\d{3,6}',f)
        if tmp:
            ser = int(tmp.group())
        else:
            ser = None
        sn.append(ser)
    return sn

def getDMCparam(fn,xyPix,xyBin,FrameIndReq=None,ut1req=None,kineticsec=None,startUTC=None,nHeadBytes=4,verbose=0):
    """
    nHeadBytes=4 for 2013-2016 data
    nHeadBytes=0 for 2011 data
    """
    Nmetadata = nHeadBytes//2 #FIXME for DMCdata version 1 only

    fn = Path(fn).expanduser()
    if not fn.is_file(): #leave this here, getsize() doesn't fail on directory
        raise ValueError('{} is not a file!'.format(fn))

    print('reading {}'.format(fn))

    #np.int64() in case we are fed a float or int
    SuperX = int64(xyPix[0]) // int64(xyBin[0]) # "//" keeps as integer
    SuperY = int64(xyPix[1]) // int64(xyBin[1])


    PixelsPerImage,BytesPerImage,BytesPerFrame = howbig(SuperX,SuperY,nHeadBytes)

    (firstRawInd,lastRawInd) = getRawInd(fn,BytesPerImage,nHeadBytes,Nmetadata)

    FrameIndRel = whichframes(fn,FrameIndReq,kineticsec,ut1req,startUTC,firstRawInd,lastRawInd,
                              BytesPerImage,BytesPerFrame,verbose)

    return {'superx':SuperX, 'supery':SuperY, 'nmetadata':Nmetadata,
            'bytesperframe':BytesPerFrame, 'pixelsperimage':PixelsPerImage,
            'nframeextract':FrameIndRel.size,
            'frameindrel':FrameIndRel}

def getNeoParam(fn,FrameIndReq=None,ut1req=None,kineticsec=None,startUTC=None,cmosinit={},verbose=False):
    """ assumption is that this is a Neo sCMOS FITS/TIFF file, where Solis chooses to break up the recordings
    into smaller files. Verify if this timing estimate makes sense for your application!
    I did not want to do regexp on the filename or USERTXT1 as I felt this too prone to error.

    inputs:
    -------
    cmosinit = {'firstrawind','lastrawind'}
    """
    fn = Path(fn).expanduser()

    nHeadBytes=0

    if fn.suffix.lower() in '.tiff':
        if tifffile is None: raise ImportError('pip install tifffile')
        #FIXME didn't the 2011 TIFFs have headers? maybe not.
        with tifffile.TiffFile(str(fn)) as f:
            data = f.asarray()
            Y,X = data.shape[-2:]
    elif fn.suffix.lower() in '.fits':
        with fits.open(str(fn),mode='readonly',memmap=False) as f:
            data = None #f[0].data  #NOTE You can read the data if you want, I didn't need it here.

            kineticsec = f[0].header['KCT']
            startseries = parse(f[0].header['DATE'] + 'Z') #TODO start of night's recording (with some Solis versionss)

            #TODO wish there was a better way
            try:
                frametxt = f[0].header['USERTXT1']
                m = re.search('(?<=Images\:)\d+-\d+(?=\.)',frametxt)
                inds = m.group(0).split('-')
            except KeyError: # just a single file?
                inds = [1,f[0].shape[0]] #yes start with 1, end without adding 1 for Andor Solis

            cmosinit={'firstrawind':int(inds[0]),
                      'lastrawind':int(inds[1])}

            #start = parse(f[0].header['FRAME']+'Z') No, incorrect by several hours with some 2015 Solis versions!

            Y,X = f[0].shape[-2:]

        startUTC = startseries.timestamp()

#%% FrameInd relative to this file
    PixelsPerImage,BytesPerImage,BytesPerFrame = howbig(X,Y,nHeadBytes)

    FrameIndRel = whichframes(fn,FrameIndReq,kineticsec,ut1req,startUTC,
                              cmosinit['firstrawind'],cmosinit['lastrawind'],
                              BytesPerImage,BytesPerFrame,verbose)

    assert isinstance(FrameIndReq,int) or FrameIndReq is None, 'TODO: add multi-frame request case'
    rawFrameInd = arange(cmosinit['firstrawind'],cmosinit['lastrawind']+1,FrameIndReq,dtype=int64)

    finf = {'superx':X,
            'supery':Y,
            'nframeextract':FrameIndRel.size,
            'nframe':rawFrameInd.size,
            'frameindrel':FrameIndRel,
            'frameind':rawFrameInd,
            'kineticsec':kineticsec}
#%% absolute frame timing (software, yikes)
    finf['ut1'] = frame2ut1(startUTC,kineticsec,rawFrameInd)

    return finf, data

def howbig(SuperX,SuperY,nHeadBytes):
    PixelsPerImage= SuperX * SuperY
    BytesPerImage = PixelsPerImage*bpp//8
    BytesPerFrame = BytesPerImage + nHeadBytes
    return PixelsPerImage,BytesPerImage,BytesPerFrame

def whichframes(fn,FrameIndReq,kineticsec,ut1req,startUTC,firstRawInd,lastRawInd,
                BytesPerImage,BytesPerFrame,verbose):
    ext = Path(fn).suffix
#%% get file size
    fileSizeBytes = fn.stat().st_size

    if fileSizeBytes < BytesPerImage:
        raise ValueError('File size {} is smaller than a single image frame!'.format(fileSizeBytes))

    if ext=='.DMCdata' and fileSizeBytes % BytesPerFrame:
        logging.error(f"Looks like I am not reading this file correctly, with BPF: {BytesPerFrame:d}")

    if ext=='.DMCdata':
        nFrame = fileSizeBytes // BytesPerFrame
        logging.info(f'{nFrame} frames, Bytes: {fileSizeBytes} in file {fn}')

        nFrameRaw = (lastRawInd-firstRawInd+1)
        if nFrameRaw != nFrame:
             logging.warning(f'there may be missed frames: nFrameRaw {nFrameRow}   nFrame {nFrame}')
    else:
        nFrame = lastRawInd-firstRawInd+1

    allrawframe = arange(firstRawInd,lastRawInd+1,1,dtype=int64)
    logging.info(f"first / last raw frame #'s: {firstRawInd}  / {lastRawInd} ")
#%% absolute time estimate
    ut1_unix_all = frame2ut1(startUTC,kineticsec,allrawframe)
#%% setup frame indices
    """
    if no requested frames were specified, read all frames. Otherwise, just
    return the requested frames
    note these assignments have to be "int64", not just python "int", because on windows python 2.7 64-bit on files >2.1GB, the bytes will wrap
    """
    FrameIndRel = ut12frame(ut1req,arange(0,nFrame,1,dtype=int64),ut1_unix_all)

    if FrameIndRel is None or len(FrameIndRel)==0: #NOTE: no ut1req or problems with ut1req, canNOT use else, need to test len() in case index is [0] validly
        FrameIndRel = req2frame(FrameIndReq, nFrame)

    badReqInd = (FrameIndRel>nFrame) | (FrameIndRel<0)
# check if we requested frames beyond what the BigFN contains
    if badReqInd.any():
        raise ValueError('You have requested frames outside the times covered in {}'.format(fn)) #don't include frames in case of None

    nFrameExtract = FrameIndRel.size #to preallocate properly
    nBytesExtract = nFrameExtract * BytesPerFrame
    if verbose > 0:
        print('Extracted {} frames from {} totaling {} bytes.'.format(nFrameExtract,fn,nBytesExtract))
    if nBytesExtract > 4e9:
        logging.info('This will require {:.2f} Gigabytes of RAM.'.format(nBytesExtract/1e9))

    return FrameIndRel


def getDMCframe(f,iFrm,finf,verbose=0):
    # on windows, "int" is int32 and overflows at 2.1GB!  We need np.int64
    currByte = iFrm * finf['bytesperframe']
#%% advance to start of frame in bytes
    if verbose>0:
        print(f'seeking to byte {currByte}')

    assert isinstance(currByte,int64),'int32 will fail on files > 2GB'
    try:
        f.seek(currByte,0) #no return value
    except IOError as e:
        raise IOError('I couldnt seek to byte {:d}. try using a 64-bit integer for iFrm \n'
              'is {} a DMCdata file?  {}'.format(currByte,f.name,e))
#%% read data ***LABVIEW USES ROW-MAJOR C ORDERING!!
    try:
        currFrame = fromfile(f, uint16,
                            finf['pixelsperimage']).reshape((finf['supery'],finf['superx']),
                            order='C')
    except ValueError as e:
        raise ValueError('we may have read past end of file?  {}'.format(e))

    rawFrameInd = meta2rawInd(f,finf['nmetadata'])

    if rawFrameInd is None: #2011 no metadata file
        rawFrameInd = iFrm+1 #fallback

    return currFrame,rawFrameInd
