#!/usr/bin/env python3
"""
reads .DMCdata files and displays them
 Michael Hirsch
 GPL v3+ license

NOTE: Observe the dtype=np.int64, this is for Windows Python, that wants to
   default to int32 instead of int64 like everyone else!
    --- we can't use long, because that's only for Python 2.7
 """
from __future__ import division, absolute_import
from os.path import getsize, expanduser, splitext, isfile
from numpy import int64,uint16,uint8,zeros,arange,fromfile,string_,atleast_1d
from re import search
from warnings import warn
from six import integer_types
from datetime import datetime
from pytz import UTC
try:
    from .timedmc import frame2ut1,ut12frame
except:
    from timedmc import frame2ut1,ut12frame

#
try:
    from matplotlib.pyplot import figure,show, hist, draw, pause
    from matplotlib.colors import LogNorm
    from matplotlib.ticker import ScalarFormatter
    #import matplotlib.animation as anim
except:
    pass
#
try:
    from . import getRawInd as gri #using from another package as submodule
except:
    import getRawInd as gri #using locally

bpp = 16
nHeadBytes = 4

def goRead(bigfn,xyPix,xyBin,FrameIndReq=None, ut1Req=None,rawFrameRate=None,startUTC=None,verbose=0):

    bigfn = expanduser(bigfn)

#%% setup data parameters
    finf = getDMCparam(bigfn,xyPix,xyBin,FrameIndReq,ut1Req,rawFrameRate,startUTC,verbose)
    if finf is None: return None, None

#%% preallocate *** LABVIEW USES ROW-MAJOR ORDERING C ORDER
    data = zeros((finf['nframeextract'],finf['supery'],finf['superx']),
                    dtype=uint16, order='C')
    rawFrameInd = zeros(finf['nframeextract'], dtype=int64)

    with open(bigfn, 'rb') as fid:
        for j,i in enumerate(finf['frameind']): #j and i are NOT the same in general when not starting from beginning of file!
            data[j,...], rawFrameInd[j] = getDMCframe(fid,i,finf,verbose)
#%% absolute time estimate
    ut1_unix = frame2ut1(startUTC,rawFrameRate,rawFrameInd)

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
        sn.append(int(search(r'(?<=CamSer)\d{3,6}',f).group()))
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

def getDMCparam(bigfn,xyPix,xyBin,FrameIndReq=None,ut1req=None,rawFrameRate=None,startUTC=None,verbose=0):
    bigfn = expanduser(bigfn)
    if not isfile(bigfn): #leave this here, getsize() doesn't fail on directory
        warn('{} is not a file!'.format(bigfn))
        return None

    #np.int64() in case we are fed a float or int
    SuperX = int64(xyPix[0]) // int64(xyBin[0]) # "//" keeps as integer
    SuperY = int64(xyPix[1]) // int64(xyBin[1])

    Nmetadata = nHeadBytes//2 #FIXME for DMCdata version 1 only
    PixelsPerImage= SuperX * SuperY
    BytesPerImage = PixelsPerImage*bpp//8
    BytesPerFrame = BytesPerImage + nHeadBytes

#%% get file size
    fileSizeBytes = getsize(bigfn)

    if fileSizeBytes < BytesPerImage:
        warn('File size {} is smaller than a single image frame!'.format(fileSizeBytes))
        return None


    if fileSizeBytes % BytesPerFrame:
        warn("Looks like I am not reading this file correctly, with BPF: {:d}".format(BytesPerFrame))

    nFrame = fileSizeBytes // BytesPerFrame

    (firstRawInd,lastRawInd) = gri.getRawInd(bigfn,BytesPerImage,nHeadBytes,Nmetadata)
    if verbose > 0:
        print('{} frames, Bytes: {} in file {}'.format(nFrame,fileSizeBytes,bigfn))
        print("first / last raw frame #'s: {}  / {} ".format(firstRawInd,lastRawInd))
#%% absolute time estimate
    allrawframe = arange(firstRawInd,lastRawInd+1,1,dtype=int64)
    nFrameRaw = (lastRawInd-firstRawInd+1)
    if nFrameRaw != nFrame:
        warn('there may be missed frames: nFrameRaw {}   nFrameBytes {}'.format(nFrameRaw,nFrame))
    ut1_unix_all = frame2ut1(startUTC,rawFrameRate,allrawframe)
#%% setup frame indices
    """
    if no requested frames were specified, read all frames. Otherwise, just
    return the requested frames
    note these assignments have to be "int64", not just python "int", because on windows python 2.7 64-bit on files >2.1GB, the bytes will wrap
    """
    FrameInd = ut12frame(ut1req,arange(0,nFrame,1,dtype=int64),ut1_unix_all)

    if FrameInd is None or len(FrameInd)==0: #NOTE: no ut1req or problems with ut1req, canNOT use else, need to test len() in case index is [0] validly
        if isinstance(FrameIndReq,integer_types): #the user is specifying a step size
            FrameInd = arange(0,nFrame,FrameIndReq,dtype=int64)
        elif FrameIndReq and len(FrameIndReq) == 3: #catch is None
            FrameInd =arange(FrameIndReq[0],FrameIndReq[1],FrameIndReq[2],dtype=int64)
        else: #catch all
            FrameInd = arange(nFrame,dtype=int64) # has to be numpy.arange for > comparison
            if verbose>0:
                print('automatically selected all frames in file')
    badReqInd = (FrameInd>nFrame) | (FrameInd<0)
# check if we requested frames beyond what the BigFN contains
    if badReqInd.any():
        warn('You have requested frames outside the times covered in {}'.format(bigfn)) #don't include frames in case of None
        return None

    nFrameExtract = FrameInd.size #to preallocate properly

    nBytesExtract = nFrameExtract * BytesPerFrame
    if verbose > 0:
        print('Extracted {} frames from {} totaling {} bytes.'.format(nFrameExtract,bigfn,nBytesExtract))
    if nBytesExtract > 4e9:
        warn('This will require {:.2f} Gigabytes of RAM.'.format(nBytesExtract/1e9))

    return {'superx':SuperX, 'supery':SuperY, 'nmetadata':Nmetadata,
            'bytesperframe':BytesPerFrame, 'pixelsperimage':PixelsPerImage,
            'nframe':nFrame, 'nframeextract':nFrameExtract,'frameind':FrameInd}

def getDMCframe(f,iFrm,finf,verbose=0):
    # on windows, "int" is int32 and overflows at 2.1GB!  We need np.int64
    currByte = iFrm * finf['bytesperframe']
#%% advance to start of frame in bytes
    if verbose>0:
        print('seeking to byte ' + str(currByte))

    assert currByte.dtype == int64
    try:
        f.seek(currByte,0) #no return value
    except IOError as e:
        warn('I couldnt seek to byte {:d}'.format(currByte))
        print('try using a 64-bit integer for iFrm')
        print('is ' + str(f.name) +' a valid .DMCdata file?')
        print(str(e))
        return None, None
#%% read data ***LABVIEW USES ROW-MAJOR C ORDERING!!
    try:
        currFrame = fromfile(f, uint16,
                            finf['pixelsperimage']).reshape((finf['supery'],finf['superx']),
                            order='C')
    except ValueError as e:
        warn('we may have read past end of file?  {}'.format(e))
        return None,None

    rawFrameInd = gri.meta2rawInd(f,finf['nmetadata'])
    return currFrame,rawFrameInd

def doPlayMovie(data,playMovie,ut1_unix=None,rawFrameInd=None,clim=None):
    if not playMovie:
        return
#%%
    sfmt = ScalarFormatter(useMathText=True)
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
    hc = hf1.colorbar(hIm,format=sfmt)
    hc.set_label('data numbers ' + str(data.dtype))
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
                hT.set_text('UT1 estimate: {}  RelFrame#: {}'.format(datetime.fromtimestamp(ut1_unix[i],tz=UTC),i))
            else:
                hT.set_text('RawFrame#: {} RelFrame# {}'.format(rawFrameInd[i],i) )
        except:
            hT.set_text('RelFrame# {}'.format(i) )

        draw(); pause(playMovie)

def doanimate(data,nFrameExtract,playMovie):
    # on some systems, just freezes at first frame
    print('attempting animation')
    fg = figure()
    ax = fg.gca()
    himg = ax.imshow(data[:,:,0],cmap='gray')
    ht = ax.set_title('')
    fg.colorbar(himg)
    ax.set_xlabel('x')
    ax.set_ylabel('y')

    #blit=False so that Title updates!
    anim.FuncAnimation(fg,animate,range(nFrameExtract),fargs=(data,himg,ht),
                       interval=playMovie, blit=False, repeat_delay=1000)

def doplotsave(bigfn,data,rawind,clim,dohist,meanImg):
    outStem = splitext(expanduser(bigfn))[0]

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

        pngfn = outStem + '_mean.png'
        print('writing mean PNG ' + pngfn)
        fg.savefig(pngfn,dpi=150,bbox_inches='tight')

def dmcconvert(finf,bigfn,data,ut1,rawind,output):
    #TODO timestamp frames
    if not output:
        return
    output=map(str.lower,output)

    stem,ext = splitext(expanduser(bigfn))
    #%% saving
    if 'h5' in output:
        """
        Reference: https://www.hdfgroup.org/HDF5/doc/ADGuide/ImageSpec.html
        Thanks to Eric Piel of Delmic for pointing out this spec
        * the HDF5 attributess set are necessary to put HDFView into image mode and enables
        other conforming readers to easily play images stacks as video.
        * the string_() calls are necessary to make fixed length strings per HDF5 spec
        """
        import h5py
        h5fn = stem + '.h5'
        print('writing {} raw image data as {}'.format(data.dtype,h5fn))
        with h5py.File(h5fn,'w',libver='latest') as f:
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
                print('writing {} frames from {} to {}'.format(data.shape[0],datetime.fromtimestamp(ut1[0]),datetime.fromtimestamp(ut1[-1])))
                fut1 = f.create_dataset('/ut1_unix',data=ut1)
                fut1.attrs['units'] = 'seconds since Unix epoch Jan 1 1970 midnight'

            if rawind is not None:
                fri = f.create_dataset('/rawind',data=rawind)
                fri.attrs['units'] = 'one-based index since camera program started this session'


    if 'fits' in output:
        from astropy.io import fits
        fitsFN = stem + '.fits'
        print('writing {} raw image data as {}'.format(data.dtype,fitsFN))

        #NOTE the with... syntax does NOT yet work with astropy.io.fits
        hdu = fits.PrimaryHDU(data)
        hdu.writeto(fitsFN,clobber=False)
        """
        Note: the orientation of this FITS in NASA FV program and the preview
        image shown in Python should/must have the same orientation and pixel indexing')
        """

    if 'mat' in output:
        from scipy.io import savemat
        matFN = stem + '.mat'
        print('writing {} raw image data as {}'.format(data.dtype,matFN))
        matdata = {'imgdata':data.transpose(1,2,0)} #matlab is fortran order
        savemat(matFN,matdata,oned_as='column')

if __name__ == "__main__":
    from argparse import ArgumentParser
    p = ArgumentParser(description='Raw .DMCdata file reader, plotter, converter')
    p.add_argument('infile',help='.DMCdata file name and path',type=str,nargs='?',default='')
    p.add_argument('-p','--pix',help='nx ny  number of x and y pixels respectively',nargs=2,default=(512,512),type=int)
    p.add_argument('-b','--bin',help='nx ny  number of x and y binning respectively',nargs=2,default=(1,1),type=int)
    p.add_argument('-f','--frames',help='frame indices of file (not raw)',nargs=3,metavar=('start','stop','stride'), type=int64) #don't use string
    p.add_argument('-m','--movie',help='seconds per frame. ',type=float)
    p.add_argument('-c','--clim',help='min max   values of intensity expected (for contrast scaling)',nargs=2,type=float)
    p.add_argument('-r','--fps',help='raw frame rate of camera',type=float)
    p.add_argument('-s','--startutc',help='utc time of nights recording')
    p.add_argument('-t','--ut1',help='UT1 times (seconds since Jan 1 1970) to request',type=float,nargs='+')
    p.add_argument('-o','--output',help='extract raw data into this type of file [h5,fits,mat]',nargs='+')
    p.add_argument('--avg',help='return the average of the requested frames, as a single image',action='store_true')
    p.add_argument('--hist',help='makes a histogram of all data frames',action='store_true')
    p.add_argument('-v','--verbose',help='debugging',action='count',default=0)
    p = p.parse_args()

    rawImgData,rawind,finf,ut1_unix = goRead(p.infile, p.pix,p.bin,p.frames,p.ut1,p.fps,p.startutc,p.verbose)
#%% convert
    dmcconvert(finf,p.infile,rawImgData,ut1_unix,rawind,p.output)
#%% plots and save
    try:
        doPlayMovie(rawImgData,p.movie, ut1_unix=ut1_unix,clim=p.clim)
        doplotsave(p.infile,rawImgData,rawind,p.clim,p.hist,p.avg)
        show()
    except Exception as e:
        print('skipped plotting  {}'.format(e))


