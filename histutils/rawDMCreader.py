#!/usr/bin/env python
"""
reads .DMCdata files and displays them
 Michael Hirsch
 GPL v3+ license

NOTE: Observe the dtype=np.int64, this is for Windows Python, that wants to
   default to int32 instead of int64 like everyone else!
 """
import logging
import re
from . import Path
from dateutil.parser import parse
from numpy import int64,uint16,uint8,zeros,arange,fromfile,string_,array
from re import search
from datetime import datetime
from pytz import UTC
from astropy.io import fits
#
from dmcutils.h5imgwriter import setupimgh5,imgwriteincr
from .timedmc import frame2ut1,ut12frame
from . import getRawInd as gri
from .common import req2frame
#
try:
    import tifffile
except:
    tifffile=None
#
bpp = 16

def goRead(bigfn,xyPix,xyBin,FrameIndReq=None, ut1Req=None,kineticraw=None,startUTC=None,cmosinit=None,verbose=0,outfn=None):

    bigfn = Path(bigfn).expanduser()
    ext = bigfn.suffix
#%% setup data parameters
    if ext == '.DMCdata':
        # preallocate *** LABVIEW USES ROW-MAJOR ORDERING C ORDER
        finf = getDMCparam(bigfn,xyPix,xyBin,FrameIndReq,ut1Req,kineticraw,startUTC,verbose)
        rawFrameInd = zeros(finf['nframeextract'], dtype=int64)
#%% output (variable or file)
        if outfn:
            setupimgh5(outfn,finf['nframeextract'],finf['supery'],finf['superx'])
            data = None
        else:
            data = zeros((finf['nframeextract'],finf['supery'],finf['superx']),
                    dtype=uint16, order='C')
#%% read
        with open(str(bigfn),'rb') as fid: #NOTE: not pathlib due to Python 2.7, Numpy 1.11 incompat. Py3.5 OK
            for j,i in enumerate(finf['frameindrel']): #j and i are NOT the same in general when not starting from beginning of file!
                D, rawFrameInd[j] = getDMCframe(fid,i,finf,verbose)
                if outfn:
                    imgwriteincr(outfn,D,j)
                else:
                    data[j,...] = D
#%% absolute time estimate, software timing (at your peril)
        finf['ut1'] = frame2ut1(startUTC,kineticraw,rawFrameInd)


    elif ext[:4] == '.tif':
        finf,data = getNeoParam(bigfn,FrameIndReq,ut1Req,kineticraw,startUTC,cmosinit,verbose)
        rawFrameInd = finf['frameind'] #FIXME this is for individual file, not start of night.



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

def getDMCparam(fn,xyPix,xyBin,FrameIndReq=None,ut1req=None,kineticsec=None,startUTC=None,verbose=0):
    nHeadBytes = 4 #FIXME for 2011-2014 data
    Nmetadata = nHeadBytes//2 #FIXME for DMCdata version 1 only

    fn = Path(fn).expanduser()
    if not fn.is_file(): #leave this here, getsize() doesn't fail on directory
        raise ValueError('{} is not a file!'.format(fn))

    #np.int64() in case we are fed a float or int
    SuperX = int64(xyPix[0]) // int64(xyBin[0]) # "//" keeps as integer
    SuperY = int64(xyPix[1]) // int64(xyBin[1])


    PixelsPerImage,BytesPerImage,BytesPerFrame = howbig(SuperX,SuperY,nHeadBytes)

    (firstRawInd,lastRawInd) = gri.getRawInd(fn,BytesPerImage,nHeadBytes,Nmetadata)

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
            SuperX,SuperY,nframe = data.shape[2], data.shape[1],data.shape[0]
    elif fn.suffix.lower() in '.fits':
        with fits.open(str(fn),mode='readonly',memmap=False) as f:
            data = None #f[0].data  #NOTE You can read the data if you want, I didn't need it here.

            kineticsec = f[0].header['KCT']
            startseries = parse(f[0].header['DATE'] + 'Z') #TODO start of night's recording (with some Solis versionss)

            #TODO this is terrible to have to do this, shame on Andor Solis authors.
            frametxt = f[0].header['USERTXT1']
            m = re.search('(?<=Images\:)\d+-\d+(?=\.)',frametxt)
            o = m.group(0).split('-')

            cmosinit={'firstrawind':int(o[0]),
                      'lastrawind':int(o[1])}

            #start = parse(f[0].header['FRAME']+'Z') No, incorrect by several hours with some 2015 Solis versions!

            nframe = f[0].header['NUMKIN']
            SuperX,SuperY = f[0].header['NAXIS1'],f[0].header['NAXIS2']

        startUTC = startseries.timestamp()

#%% FrameInd relative to this file
    PixelsPerImage,BytesPerImage,BytesPerFrame = howbig(SuperX,SuperY,nHeadBytes)

    FrameIndRel = whichframes(fn,FrameIndReq,kineticsec,ut1req,startUTC,
                              cmosinit['firstrawind'],cmosinit['lastrawind'],
                              BytesPerImage,BytesPerFrame,verbose)

    assert isinstance(FrameIndReq,int) or FrameIndReq is None, 'TODO: add multi-frame request case'
    rawFrameInd = arange(cmosinit['firstrawind'],cmosinit['lastrawind']+1,FrameIndReq,dtype=int64)

    finf = {'superx':SuperX,
            'supery':SuperY,
            'nframeextract':nframe,
            'nframe':nframe,
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
        logging.error("Looks like I am not reading this file correctly, with BPF: {:d}".format(BytesPerFrame))

    if ext=='.DMCdata':
        nFrame = fileSizeBytes // BytesPerFrame
        logging.info('{} frames, Bytes: {} in file {}'.format(nFrame,fileSizeBytes, fn))

        nFrameRaw = (lastRawInd-firstRawInd+1)
        if nFrameRaw != nFrame:
             logging.warning('there may be missed frames: nFrameRaw {}   nFrameBytes {}'.format(nFrameRaw,nFrame))
    else:
        nFrame = lastRawInd-firstRawInd+1

    allrawframe = arange(firstRawInd,lastRawInd+1,1,dtype=int64)
    logging.info("first / last raw frame #'s: {}  / {} ".format(firstRawInd,lastRawInd))
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
        print('seeking to byte ' + str(currByte))

    assert isinstance(currByte,int64)
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

    rawFrameInd = gri.meta2rawInd(f,finf['nmetadata'])
    return currFrame,rawFrameInd

def dmcconvert(data,ut1,rawind,outfn,params,cmdlog=''):
    if not outfn:
        return

    outfn = Path(outfn).expanduser()
    #%% saving
    if outfn.suffix == '.h5':
        """
        Reference: https://www.hdfgroup.org/HDF5/doc/ADGuide/ImageSpec.html
        Thanks to Eric Piel of Delmic for pointing out this spec
        * the HDF5 attributess set are necessary to put HDFView into image mode and enables
        other conforming readers to easily play images stacks as video.
        * the string_() calls are necessary to make fixed length strings per HDF5 spec
        """

        import h5py
        #NOTE write mode r+ to not overwrite incremental images
        with h5py.File(str(outfn),'r+',libver='latest') as f:
            if data is not None:
                fimg = f.create_dataset('/rawimg',data=data,
                             compression='gzip',
                             compression_opts=1, #no difference in size from 1 to 5, except much faster to use lower numbers!
                             shuffle=True,
                             fletcher32=True,
                             track_times=True)
                fimg.attrs["CLASS"] = string_("IMAGE")
                fimg.attrs["IMAGE_VERSION"] = string_("1.2")
                fimg.attrs["IMAGE_SUBCLASS"] = string_("IMAGE_GRAYSCALE")
                fimg.attrs["DISPLAY_ORIGIN"] = string_("LL")
                fimg.attrs['IMAGE_WHITE_IS_ZERO'] = uint8(0)

            if ut1 is not None: #needs is not None
                try:
                    print('writing from {} to {}'.format(datetime.utcfromtimestamp(ut1[0]).replace(tzinfo=UTC),
                                                                   datetime.utcfromtimestamp(ut1[-1]).replace(tzinfo=UTC)))
                    fut1 = f.create_dataset('/ut1_unix',data=ut1,fletcher32=True)
                    fut1.attrs['units'] = 'seconds since Unix epoch Jan 1 1970 midnight'
                except Exception as e:
                    print(e)

            if rawind is not None:
                try:
                    fri = f.create_dataset('/rawind',data=rawind)
                    fri.attrs['units'] = 'one-based index since camera program started this session'
                except Exception as e:
                    logging.error(e)

            try:
                cparam = array((params['kineticsec'],
                            params['rotccw'],
                            params['transpose']==True,
                            params['flipud']==True,
                            params['fliplr']==True,
                            1),
                           dtype=[('kineticsec','f8'),
                                  ('rotccw',    'i1'),
                                  ('transpose', 'i1'),
                                  ('flipud',    'i1'),
                                  ('fliplr',    'i1'),
                                  ('questionable_ut1','i1')]
                           )

                f.create_dataset('/params',data=cparam) #cannot use fletcher32 here, typeerror
            except Exception as e:
                logging.error(e)

            try:
                l = params['sensorloc']
                lparam = array((l[0],l[1],l[2]),     dtype=[('lat','f8'),('lon','f8'),('alt_m','f8')])

                Ld = f.create_dataset('/sensorloc',data=lparam) #cannot use fletcher32 here, typeerror
                Ld.attrs['units'] = 'WGS-84 lat (deg),lon (deg), altitude (meters)'
            except TypeError:
                pass
            except Exception as e:
                logging.error('sensorloc  {}'.format(e))

            if isinstance(cmdlog,(tuple,list)):
                cmdlog = ' '.join(cmdlog)
            f.create_dataset('/cmdlog',data=str(cmdlog)) #cannot use fletcher32 here, typeerror

    elif outfn.suffix == '.fits':
        from astropy.io import fits
        #NOTE the with... syntax does NOT yet work with astropy.io.fits
        hdu = fits.PrimaryHDU(data)
        hdu.writeto(outfn,clobber=False,checksum=True)
        #no close
        """
        Note: the orientation of this FITS in NASA FV program and the preview
        image shown in Python should/must have the same orientation and pixel indexing')
        """

    elif outfn.suffix == '.mat':
        from scipy.io import savemat
        matdata = {'imgdata':data.transpose(1,2,0)} #matlab is fortran order
        savemat(outfn,matdata,oned_as='column')
