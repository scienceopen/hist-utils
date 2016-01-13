#!/usr/bin/env python3
"""
reads .DMCdata files and displays them
 Michael Hirsch
 GPL v3+ license

NOTE: Observe the dtype=np.int64, this is for Windows Python, that wants to
   default to int32 instead of int64 like everyone else!
 """
import logging
from pathlib import Path
from numpy import int64,uint16,uint8,zeros,arange,fromfile,string_,array
from re import search
from datetime import datetime
from pytz import UTC
#
from .timedmc import frame2ut1,ut12frame
from . import getRawInd as gri
#
try:
    from matplotlib.pyplot import figure, hist, draw, pause
    from matplotlib.colors import LogNorm
    #from matplotlib.ticker import ScalarFormatter
    #import matplotlib.animation as anim
except:
    pass
#
try:
    import tifffile
except:
    logging.warning('unable to read tiff files,   pip install tifffile')
#
bpp = 16

def goRead(bigfn,xyPix,xyBin,FrameIndReq=None, ut1Req=None,kineticraw=None,startUTC=None,cmosinit=None,verbose=0):

    bigfn = Path(bigfn).expanduser()
    ext = bigfn.suffix
#%% setup data parameters
    if ext == '.DMCdata':
        # preallocate *** LABVIEW USES ROW-MAJOR ORDERING C ORDER
        finf = getDMCparam(bigfn,xyPix,xyBin,FrameIndReq,ut1Req,kineticraw,startUTC,verbose)
        data = zeros((finf['nframeextract'],finf['supery'],finf['superx']),
                    dtype=uint16, order='C')
        rawFrameInd = zeros(finf['nframeextract'], dtype=int64)
        # read
        with bigfn.open('rb') as fid:
            for j,i in enumerate(finf['frameindrel']): #j and i are NOT the same in general when not starting from beginning of file!
                data[j,...], rawFrameInd[j] = getDMCframe(fid,i,finf,verbose)

    elif ext[:4] == '.tif':
        finf,data,rawFrameInd = getTIFparam(bigfn,FrameIndReq,ut1Req,kineticraw,startUTC,cmosinit,verbose)


#%% absolute time estimate
    ut1_unix = frame2ut1(startUTC,kineticraw,rawFrameInd)

    return data, rawFrameInd,finf,ut1_unix
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

def animate(i,data,himg,ht):
    #himg = plt.imshow(data[:,:,i]) #slow, use set_data instead
    himg.set_data(data[i,:,:])
    ht.set_text('RelFrame#' + str(i) )
    #'RawFrame#: ' + str(rawFrameInd[jFrm]) +

    draw() #plot won't update without plt.draw()!
    #plt.pause(0.01)
    #plt.show(False) #breaks (won't play)
    return himg,ht


def getDMCparam(bigfn,xyPix,xyBin,FrameIndReq=None,ut1req=None,kineticsec=None,startUTC=None,verbose=0):
    nHeadBytes = 4 #FIXME for 2011-2014 data
    Nmetadata = nHeadBytes//2 #FIXME for DMCdata version 1 only

    bigfn = Path(bigfn)
    if not bigfn.is_file(): #leave this here, getsize() doesn't fail on directory
        raise ValueError('{} is not a file!'.format(bigfn))

    #np.int64() in case we are fed a float or int
    SuperX = int64(xyPix[0]) // int64(xyBin[0]) # "//" keeps as integer
    SuperY = int64(xyPix[1]) // int64(xyBin[1])


    PixelsPerImage,BytesPerImage,BytesPerFrame = howbig(SuperX,SuperY,nHeadBytes)

    (firstRawInd,lastRawInd) = gri.getRawInd(bigfn,BytesPerImage,nHeadBytes,Nmetadata)

    FrameIndRel = whichframes(bigfn,FrameIndReq,kineticsec,ut1req,startUTC,firstRawInd,lastRawInd,
                              BytesPerImage,BytesPerFrame,verbose)

    return {'superx':SuperX, 'supery':SuperY, 'nmetadata':Nmetadata,
            'bytesperframe':BytesPerFrame, 'pixelsperimage':PixelsPerImage,
            'nframeextract':FrameIndRel.size,
            'frameindrel':FrameIndRel}

def getTIFparam(bigfn,FrameIndReq,ut1req,kineticsec,startUTC,cmosinit,verbose):
    """ assumption is that this is a Neo sCMOS file, where Solis chooses to break up the recordings
    into smaller files. Verify if this timing estimate makes sense for your application!
    I did not want to do regexp on the filename or USERTXT1 as I felt this too prone to error.
    This function should be rarely enough used that it's worth the user knowing what they're doing.

    inputs:
    -------
    cmosinit = {'firstrawind','lastrawind'}
    """
    nHeadBytes=0

    with tifffile.TiffFile(bigfn) as tif:
        data = tif.asarray()

    if data.ndim != 3:
       logging.error('Im not sure what sort of tiff {} youre reading, I expect to read a 3-D array page x height x width'.format(bigfn))

    SuperX = data.shape[2]
    SuperY = data.shape[1]

#%% FrameInd relative to this file

    PixelsPerImage,BytesPerImage,BytesPerFrame = howbig(SuperX,SuperY,nHeadBytes)

    FrameIndRel = whichframes(bigfn,FrameIndReq,kineticsec,ut1req,startUTC,
                              cmosinit['firstrawind'],cmosinit['lastrawind'],
                              BytesPerImage,BytesPerFrame,verbose)

    rawFrameInd = arange(cmosinit['firstrawind'],cmosinit['lastrawind']+1,1,dtype=int64)

    return {'superx':SuperX,
            'supery':SuperY,
            'nframeextract':data.shape[0],
            'frameindrel':FrameIndRel}, data, rawFrameInd

def howbig(SuperX,SuperY,nHeadBytes):
    PixelsPerImage= SuperX * SuperY
    BytesPerImage = PixelsPerImage*bpp//8
    BytesPerFrame = BytesPerImage + nHeadBytes
    return PixelsPerImage,BytesPerImage,BytesPerFrame

def whichframes(bigfn,FrameIndReq,kineticsec,ut1req,startUTC,firstRawInd,lastRawInd,
                BytesPerImage,BytesPerFrame,verbose):
    ext = Path(bigfn).suffix
#%% get file size
    fileSizeBytes = bigfn.stat().st_size

    if fileSizeBytes < BytesPerImage:
        raise ValueError('File size {} is smaller than a single image frame!'.format(fileSizeBytes))

    if ext=='.DMCdata' and fileSizeBytes % BytesPerFrame:
        logging.error("Looks like I am not reading this file correctly, with BPF: {:d}".format(BytesPerFrame))

    nFrame = fileSizeBytes // BytesPerFrame

    logging.info('{} frames, Bytes: {} in file {}'.format(nFrame,fileSizeBytes,bigfn))
    logging.info("first / last raw frame #'s: {}  / {} ".format(firstRawInd,lastRawInd))
#%% absolute time estimate
    allrawframe = arange(firstRawInd,lastRawInd+1,1,dtype=int64)
    nFrameRaw = (lastRawInd-firstRawInd+1)
    if nFrameRaw != nFrame:
        logging.warning('there may be missed frames: nFrameRaw {}   nFrameBytes {}'.format(nFrameRaw,nFrame))
    ut1_unix_all = frame2ut1(startUTC,kineticsec,allrawframe)
#%% setup frame indices
    """
    if no requested frames were specified, read all frames. Otherwise, just
    return the requested frames
    note these assignments have to be "int64", not just python "int", because on windows python 2.7 64-bit on files >2.1GB, the bytes will wrap
    """
    FrameIndRel = ut12frame(ut1req,arange(0,nFrame,1,dtype=int64),ut1_unix_all)

    if FrameIndRel is None or len(FrameIndRel)==0: #NOTE: no ut1req or problems with ut1req, canNOT use else, need to test len() in case index is [0] validly
        if isinstance(FrameIndReq,int): #the user is specifying a step size
            FrameIndRel = arange(0,nFrame,FrameIndReq,dtype=int64)
        elif FrameIndReq and len(FrameIndReq) == 3: #catch is None
            # this is -1 because user is specifying one-based index
            FrameIndRel =arange(FrameIndReq[0],FrameIndReq[1],FrameIndReq[2],dtype=int64)-1 #keep -1 !
        else: #catch all
            FrameIndRel = arange(nFrame,dtype=int64) # has to be numpy.arange for > comparison
            if verbose>0:
                print('automatically selected all frames in file')
    badReqInd = (FrameIndRel>nFrame) | (FrameIndRel<0)
# check if we requested frames beyond what the BigFN contains
    if badReqInd.any():
        raise ValueError('You have requested frames outside the times covered in {}'.format(bigfn)) #don't include frames in case of None

    nFrameExtract = FrameIndRel.size #to preallocate properly
    nBytesExtract = nFrameExtract * BytesPerFrame
    if verbose > 0:
        print('Extracted {} frames from {} totaling {} bytes.'.format(nFrameExtract,bigfn,nBytesExtract))
    if nBytesExtract > 4e9:
        logging.warning('This will require {:.2f} Gigabytes of RAM.'.format(nBytesExtract/1e9))

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

def doPlayMovie(data,playMovie,ut1_unix=None,rawFrameInd=None,clim=None):
    if not playMovie:
        return
#%%
    #sfmt = ScalarFormatter(useMathText=True)
    hf1 = figure(1)
    hAx = hf1.gca()

    try:
        hIm = hAx.imshow(data[0,...],
                vmin=clim[0],vmax=clim[1],
                cmap = 'gray', origin='lower', norm=LogNorm())
    except: #clim wasn't specified properly
        print('setting image viewing limits based on first frame')
        hIm = hAx.imshow(data[0,...], cmap = 'gray', origin='lower',norm=LogNorm() )

    hT = hAx.text(0.5,1.005,'', ha='center',transform=hAx.transAxes)
    #hc = hf1.colorbar(hIm,format=sfmt)
    #hc.set_label('data numbers ' + str(data.dtype))
    hAx.set_xlabel('x-pixels')
    hAx.set_ylabel('y-pixels')

    if ut1_unix is not None:
        titleut=True
    else:
        titleut=False

    for i,d in enumerate(data):
        hIm.set_data(d)
        try:
            if titleut:
                hT.set_text('UT1 estimate: {}  RelFrame#: {}'.format(datetime.utcfromtimestamp(ut1_unix[i]).replace(tzinfo=UTC),i))
            else:
                hT.set_text('RawFrame#: {} RelFrame# {}'.format(rawFrameInd[i],i) )
        except:
            hT.set_text('RelFrame# {}'.format(i) )

        draw(); pause(playMovie)

#def doanimate(data,nFrameExtract,playMovie):
#    # on some systems, just freezes at first frame
#    print('attempting animation')
#    fg = figure()
#    ax = fg.gca()
#    himg = ax.imshow(data[:,:,0],cmap='gray')
#    ht = ax.set_title('')
#    fg.colorbar(himg)
#    ax.set_xlabel('x')
#    ax.set_ylabel('y')
#
#    #blit=False so that Title updates!
#    anim.FuncAnimation(fg,animate,range(nFrameExtract),fargs=(data,himg,ht),
#                       interval=playMovie, blit=False, repeat_delay=1000)

def doplotsave(bigfn,data,rawind,clim,dohist,meanImg):
    bigfn=Path(bigfn)

    if dohist:
        ax=figure().gca()
        hist(data.ravel(), bins=256,log=True)
        ax.set_title('histogram of {}'.format(bigfn))
        ax.set_ylabel('frequency of occurence')
        ax.set_xlabel('data value')

    if meanImg:
        meanStack = data.mean(axis=0).astype(uint16) #DO NOT use dtype= here, it messes up internal calculation!
        fg = figure(32)
        ax = fg.gca()
        if clim:
            hi=ax.imshow(meanStack,cmap='gray',origin='lower', vmin=clim[0], vmax=clim[1],norm=LogNorm())
        else:
            hi=ax.imshow(meanStack,cmap='gray',origin='lower',norm=LogNorm())

        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('mean of image frames')
        fg.colorbar(hi)

        pngfn = bigfn.with_suffix('_mean.png')
        print('writing mean PNG ' + pngfn)
        fg.savefig(pngfn,dpi=150,bbox_inches='tight')

def dmcconvert(data,ut1,rawind,outfn,params):
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
        with h5py.File(str(outfn),'w',libver='latest') as f:
            if data is not None:
                fimg = f.create_dataset('/rawimg',data=data,
                             compression='gzip',
                             compression_opts=4,
                             track_times=True)
                fimg.attrs["CLASS"] = string_("IMAGE")
                fimg.attrs["IMAGE_VERSION"] = string_("1.2")
                fimg.attrs["IMAGE_SUBCLASS"] = string_("IMAGE_GRAYSCALE")
                fimg.attrs["DISPLAY_ORIGIN"] = string_("LL")
                fimg.attrs['IMAGE_WHITE_IS_ZERO'] = uint8(0)

            if ut1 is not None: #needs is not None
                print('writing from {} to {}'.format(datetime.utcfromtimestamp(ut1[0]).replace(tzinfo=UTC),
                                                               datetime.utcfromtimestamp(ut1[-1]).replace(tzinfo=UTC)))
                fut1 = f.create_dataset('/ut1_unix',data=ut1)
                fut1.attrs['units'] = 'seconds since Unix epoch Jan 1 1970 midnight'

            if rawind is not None:
                fri = f.create_dataset('/rawind',data=rawind)
                fri.attrs['units'] = 'one-based index since camera program started this session'


            cparam = array((params['kineticsec'],
                            params['rotccw'],
                            params['transpose']==True,
                            params['flipud']==True,
                            params['fliplr']==True,
                            params['fire'] is None),
                           dtype=[('kineticsec','f8'),
                                  ('rotccw',    'i1'),
                                  ('transpose', 'i1'),
                                  ('flipud',    'i1'),
                                  ('fliplr',    'i1'),
                                  ('questionable_ut1','i1')]
                           )

            f.create_dataset('/params',data=cparam)

    elif outfn.suffix == '.fits':
        from astropy.io import fits
        #NOTE the with... syntax does NOT yet work with astropy.io.fits
        hdu = fits.PrimaryHDU(data)
        hdu.writeto(outfn,clobber=False)
        #no close
        """
        Note: the orientation of this FITS in NASA FV program and the preview
        image shown in Python should/must have the same orientation and pixel indexing')
        """

    elif outfn.suffix == '.mat':
        from scipy.io import savemat
        matdata = {'imgdata':data.transpose(1,2,0)} #matlab is fortran order
        savemat(outfn,matdata,oned_as='column')
