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
from numpy import int64, uint16, zeros, arange, fromfile
import numpy as np
from re import search
from astropy.io import fits
#
from . import req2frame, dir2fn, getRawInd, meta2rawInd, setupimgh5, imgwriteincr, write_quota
from .timedmc import frame2ut1, ut12frame
#
try:
    import tifffile
except ImportError:
    tifffile = None
#
bpp = 16


def goRead(fn: Path,
           xyPix, xyBin,
           FrameIndReq=None, ut1Req=None, kineticraw=None,
           startUTC=None, cmosinit=None, verbose=0, outfn=None, nHeadBytes: int=4):

    fn = Path(fn).expanduser()
    ext = fn.suffix
# %% optional output file setup
    outfn = dir2fn(outfn, fn, '.h5')
# %% setup data parameters
    data: np.ndarray
    if ext in ('.DMCdata', '.dat'):
        # preallocate *** LABVIEW USES ROW-MAJOR ORDERING C ORDER
        finf = getDMCparam(fn, xyPix, xyBin, FrameIndReq,
                           ut1Req, kineticraw, startUTC, nHeadBytes, verbose)
        write_quota(finf['bytesperframe'] * finf['nframeextract'], outfn)

        rawFrameInd = zeros(finf['nframeextract'], dtype=int64)
# %% output (variable or file)
        if outfn:
            setupimgh5(outfn, finf['nframeextract'],
                       finf['supery'], finf['superx'])
            data = None
        else:
            data = zeros((finf['nframeextract'], finf['supery'], finf['superx']),
                         dtype=uint16, order='C')
# %% read
        # NOTE: not pathlib due to Python 2.7, Numpy 1.11 incompat. Py3.5 OK
        with fn.open('rb') as fid:
            # j and i are NOT the same in general when not starting from beginning of file!
            for j, i in enumerate(finf['frameindrel']):
                D, rawFrameInd[j] = getDMCframe(fid, i, finf, verbose)
                if outfn:
                    imgwriteincr(outfn, D, j)
                else:
                    data[j, ...] = D
# %% absolute time estimate, software timing (at your peril)
        finf['ut1'] = frame2ut1(startUTC, kineticraw, rawFrameInd)

    elif ext[:4] == '.tif':
        finf = getNeoParam(fn, FrameIndReq, ut1Req,
                           kineticraw, startUTC, cmosinit, verbose)
        # FIXME this is for individual file, not start of night.
        rawFrameInd = finf['frameind']
        data = None  # just didn't need this right now.
    else:
        raise ValueError(f'not sure to do with file {fn}')

    return data, rawFrameInd, finf  # ,ut1_unix
# %% workers


def getserialnum(flist):
    """
    This function assumes the serial number of the camera is in a particular place in the filename.
    Yes, this is a little lame, but it's how the original 2011 image-writing program worked, and I've
    carried over the scheme rather than appending bits to dozens of TB of files.
    """
    sn = []
    for f in flist:
        tmp = search(r'(?<=CamSer)\d{3,6}', f)
        if tmp:
            ser = int(tmp.group())
        else:
            ser = None
        sn.append(ser)
    return sn


def getDMCparam(fn: Path, xyPix, xyBin,
                FrameIndReq=None, ut1req=None, kineticsec=None, startUTC=None, nHeadBytes=4, verbose=0):
    """
    nHeadBytes=4 for 2013-2016 data
    nHeadBytes=0 for 2011 data
    """
    Nmetadata = nHeadBytes // 2  # FIXME for DMCdata version 1 only

    if not fn.is_file():  # leave this here, getsize() doesn't fail on directory
        raise ValueError(f'{fn} is not a file!')

    print(f'reading {fn}')

    # int() in case we are fed a float or int
    SuperX = int(xyPix[0] // xyBin[0])
    SuperY = int(xyPix[1] // xyBin[1])

    PixelsPerImage, BytesPerImage, BytesPerFrame = howbig(
        SuperX, SuperY, nHeadBytes)

    (firstRawInd, lastRawInd) = getRawInd(
        fn, BytesPerImage, nHeadBytes, Nmetadata)

    FrameIndRel = whichframes(fn, FrameIndReq, kineticsec, ut1req, startUTC, firstRawInd, lastRawInd,
                              BytesPerImage, BytesPerFrame, verbose)

    return {'superx': SuperX, 'supery': SuperY, 'nmetadata': Nmetadata,
            'bytesperframe': BytesPerFrame, 'pixelsperimage': PixelsPerImage,
            'nframeextract': FrameIndRel.size,
            'frameindrel': FrameIndRel}


def getNeoParam(fn, FrameIndReq=None, ut1req=None, kineticsec=None, startUTC=None, cmosinit={}, verbose=False):
    """ assumption is that this is a Neo sCMOS FITS/TIFF file, where Solis chooses to break up the recordings
    into smaller files. Verify if this timing estimate makes sense for your application!
    I did not want to do regexp on the filename or USERTXT1 as I felt this too prone to error.

    inputs:
    -------
    cmosinit = {'firstrawind','lastrawind'}
    """
    fn = Path(fn).expanduser()

    nHeadBytes = 0

    if fn.suffix.lower() in '.tiff':
        if tifffile is None:
            raise ImportError('pip install tifffile')
        # FIXME didn't the 2011 TIFFs have headers? maybe not.
        with tifffile.TiffFile(str(fn)) as f:
            Y, X = f[0].shape
            cmosinit = {'firstrawind': 1,
                        'lastrawind': len(f)}
    elif fn.suffix.lower() in '.fits':
        with fits.open(fn, mode='readonly', memmap=False) as f:

            kineticsec = f[0].header['KCT']
            # TODO start of night's recording (with some Solis versionss)
            startseries = parse(f[0].header['DATE'] + 'Z')

            # TODO wish there was a better way
            try:
                frametxt = f[0].header['USERTXT1']
                m = re.search('(?<=Images\:)\d+-\d+(?=\.)', frametxt)
                inds = m.group(0).split('-')
            except KeyError:  # just a single file?
                # yes start with 1, end without adding 1 for Andor Solis
                inds = [1, f[0].shape[0]]

            cmosinit = {'firstrawind': int(inds[0]),
                        'lastrawind': int(inds[1])}

            # start = parse(f[0].header['FRAME']+'Z') No, incorrect by several hours with some 2015 Solis versions!

            Y, X = f[0].shape[-2:]

        startUTC = startseries.timestamp()

# %% FrameInd relative to this file
    PixelsPerImage, BytesPerImage, BytesPerFrame = howbig(X, Y, nHeadBytes)

    FrameIndRel = whichframes(fn, FrameIndReq, kineticsec, ut1req, startUTC,
                              cmosinit['firstrawind'], cmosinit['lastrawind'],
                              BytesPerImage, BytesPerFrame, verbose)

    assert isinstance(
        FrameIndReq, int) or FrameIndReq is None, 'TODO: add multi-frame request case'
    rawFrameInd = arange(cmosinit['firstrawind'],
                         cmosinit['lastrawind'] + 1,
                         FrameIndReq, dtype=int64)

    finf = {'superx': X,
            'supery': Y,
            'nframeextract': FrameIndRel.size,
            'nframe': rawFrameInd.size,
            'frameindrel': FrameIndRel,
            'frameind': rawFrameInd,
            'kineticsec': kineticsec}
# %% absolute frame timing (software, yikes)
    finf['ut1'] = frame2ut1(startUTC, kineticsec, rawFrameInd)

    return finf


def howbig(SuperX, SuperY, nHeadBytes):
    PixelsPerImage = SuperX * SuperY
    BytesPerImage = PixelsPerImage * bpp // 8
    BytesPerFrame = BytesPerImage + nHeadBytes
    return PixelsPerImage, BytesPerImage, BytesPerFrame


def whichframes(fn, FrameIndReq, kineticsec, ut1req, startUTC, firstRawInd, lastRawInd,
                BytesPerImage, BytesPerFrame, verbose):
    ext = Path(fn).suffix
# %% get file size
    fileSizeBytes = fn.stat().st_size

    if fileSizeBytes < BytesPerImage:
        raise ValueError(
            f'File size {fileSizeBytes} is smaller than a single image frame!')

    if ext == '.DMCdata' and fileSizeBytes % BytesPerFrame:
        logging.error(
            f"Looks like I am not reading this file correctly, with BPF: {BytesPerFrame:d}")

    if ext == '.DMCdata':
        nFrame = fileSizeBytes // BytesPerFrame
        print(f'{nFrame} frames, Bytes: {fileSizeBytes} in file {fn}')

        nFrameRaw = (lastRawInd - firstRawInd + 1)
        if nFrameRaw != nFrame:
            logging.warning(
                f'there may be missed frames: nFrameRaw {nFrameRaw}   nFrame {nFrame}')
    else:
        nFrame = lastRawInd - firstRawInd + 1

    allrawframe = arange(firstRawInd, lastRawInd + 1, 1, dtype=int64)
    print(f"first / last raw frame #'s: {firstRawInd}  / {lastRawInd} ")
# %% absolute time estimate
    ut1_unix_all = frame2ut1(startUTC, kineticsec, allrawframe)
# %% setup frame indices
    """
    if no requested frames were specified, read all frames. Otherwise, just
    return the requested frames
    note these assignments have to be "int64", not just python "int", because on windows python 2.7 64-bit on files >2.1GB, the bytes will wrap
    """
    FrameIndRel = ut12frame(ut1req,
                            arange(0, nFrame, 1, dtype=int64),
                            ut1_unix_all)

    # NOTE: no ut1req or problems with ut1req, canNOT use else, need to test len() in case index is [0] validly
    if FrameIndRel is None or len(FrameIndRel) == 0:
        FrameIndRel = req2frame(FrameIndReq, nFrame)

    badReqInd = (FrameIndRel > nFrame) | (FrameIndRel < 0)
# check if we requested frames beyond what the BigFN contains
    if badReqInd.any():
        # don't include frames in case of None
        raise ValueError(f'frames requested outside the times covered in {fn}')

    nFrameExtract = FrameIndRel.size  # to preallocate properly
    nBytesExtract = nFrameExtract * BytesPerFrame
    print(
        f'Extracted {nFrameExtract} frames from {fn} totaling {nBytesExtract/1e9:.2f} GB.')

    if nBytesExtract > 4e9:
        print(f'This will require {nBytesExtract/1e9:.2f} GB of RAM.')

    return FrameIndRel


def getDMCframe(f, iFrm: int, finf: dict, verbose: bool=False):
    """
    f is open file handle
    """
    # on windows, "int" is int32 and overflows at 2.1GB!  We need np.int64
    currByte = iFrm * finf['bytesperframe']
# %% advance to start of frame in bytes
    if verbose:
        print(f'seeking to byte {currByte}')

    assert isinstance(iFrm, (int, int64)), 'int32 will fail on files > 2GB'

    try:
        f.seek(currByte, 0)
    except IOError as e:
        raise IOError(f'I couldnt seek to byte {currByte:d}. try using a 64-bit integer for iFrm \n'
                      'is {f.name} a DMCdata file?  {e}')
# %% read data ***LABVIEW USES ROW-MAJOR C ORDERING!!
    try:
        currFrame = fromfile(f, uint16,
                             finf['pixelsperimage']).reshape((finf['supery'], finf['superx']),
                                                             order='C')
    except ValueError as e:
        raise ValueError(f'read past end of file?  {e}')

    rawFrameInd = meta2rawInd(f, finf['nmetadata'])

    if rawFrameInd is None:  # 2011 no metadata file
        rawFrameInd = iFrm + 1  # fallback

    return currFrame, rawFrameInd
