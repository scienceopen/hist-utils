#!/usr/bin/env python3
"""
reads .DMCdata files and displays them
 Michael Hirsch
 GPL v3+ license

NOTE: Observe the dtype=np.int64, this is for Windows Python, that wants to
   default to int32 instead of int64 like everyone else!
    --- we can't use long, because that's only for Python 2.7
 """
from __future__ import division, print_function, absolute_import
from os.path import getsize, expanduser, splitext, isfile
import numpy as np
import argparse
from re import search
from warnings import warn
from six import integer_types
#
try:
    from . import getRawInd as gri #using from another package as submodule
except (ValueError,SystemError):
    import getRawInd as gri #using locally

bpp = 16
nHeadBytes = 4

def goRead(bigfn,xyPix,xyBin,FrameIndReq=None, rawFrameRate=None,startUTC=None,verbose=0):

    bigfn = expanduser(bigfn)
#%% check
    if startUTC:
        raise NotImplementedError('frame UTC timing not yet implemented')
    if rawFrameRate:
        raise NotImplementedError('raw frame rate timing not yet implemented')
#%% setup data parameters
    finf = getDMCparam(bigfn,xyPix,xyBin,FrameIndReq,verbose)
    if finf is None: return None, None

#%% preallocate *** LABVIEW USES ROW-MAJOR ORDERING C ORDER
    data = np.zeros((finf['nframeextract'],finf['supery'],finf['superx']),
                    dtype=np.uint16, order='C')
    rawFrameInd = np.zeros(finf['nframeextract'], dtype=np.int64)

    with open(bigfn, 'rb') as fid:
        for j,i in enumerate(finf['frameind']): #j and i are NOT the same in general when not starting from beginning of file!
            data[j,:,:], rawFrameInd[j] = getDMCframe(fid,i,finf,verbose)

    return data, rawFrameInd,finf
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

def getDMCparam(bigfn,xyPix,xyBin,FrameIndReq=None,verbose=0):
    bigfn = expanduser(bigfn)
    if not isfile(bigfn): #leave this here, getsize() doesn't fail on directory
        warn('{} is not a file!'.format(bigfn))
        return None

    #np.int64() in case we are fed a float or int
    SuperX = np.int64(xyPix[0]) // np.int64(xyBin[0]) # "//" keeps as integer
    SuperY = np.int64(xyPix[1]) // np.int64(xyBin[1])

    Nmetadata = nHeadBytes//2 #FIXME for DMCdata version 1 only
    PixelsPerImage= SuperX * SuperY
    BytesPerImage = PixelsPerImage*bpp//8
    BytesPerFrame = BytesPerImage + nHeadBytes

# get file size
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

# setup frame indices
# if no requested frames were specified, read all frames. Otherwise, just
# return the requested frames
    #note these assignments have to be "long", not just python "int", because on windows python 2.7 64-bit on files >2.1GB, the bytes will wrap
    if isinstance(FrameIndReq,integer_types): #the user is specifying a step size
        FrameInd =np.arange(0,nFrame,FrameIndReq,dtype=np.int64)
    elif FrameIndReq and len(FrameIndReq) == 3: #catch is None
        FrameInd =np.arange(FrameIndReq[0],FrameIndReq[1],FrameIndReq[2],dtype=np.int64)
    else: #catch all
        FrameInd = np.arange(nFrame,dtype=np.int64) # has to be numpy.arange for > comparison
        if verbose>0:
            print('automatically selected all frames in file')
    badReqInd = (FrameInd>nFrame) | (FrameInd<0)
# check if we requested frames beyond what the BigFN contains
    if badReqInd.any():
        warn('You have requested Frames ' + str(FrameInd[badReqInd]) +
                 ', which exceeds the length of {}'.format(bigfn))
        return None

    nFrameExtract = FrameInd.size #to preallocate properly

    nBytesExtract = nFrameExtract * BytesPerFrame
    if verbose > 0:
        print('Extracted {} frames from {} totaling {} bytes.'.format(
                   nFrameExtract,bigfn,nBytesExtract))
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

    assert currByte.dtype == np.int64
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
        currFrame = np.fromfile(f, np.uint16,
                            finf['pixelsperimage']).reshape((finf['supery'],finf['superx']),
                            order='C')
    except ValueError as e:
        warn('we may have read past end of file?  {}'.format(e))
        return None,None

    rawFrameInd = gri.meta2rawInd(f,finf['nmetadata'])
    return currFrame,rawFrameInd

def doPlayMovie(data,finf,playMovie,Clim,rawFrameInd):
    if playMovie:
        sfmt = ScalarFormatter(useMathText=True)
        hf1 = figure(1)
        hAx = hf1.gca()
        if Clim is None:
            hIm = hAx.imshow(data[0,:,:], cmap = 'gray', origin='lower',norm=LogNorm() )
        else:
            hIm = hAx.imshow(data[0,:,:],
                            vmin=Clim[0],vmax=Clim[1],
                            cmap = 'gray', origin='lower', norm=LogNorm())
        hT = hAx.text(0.5,1.005,'', ha='center',transform=hAx.transAxes)
        hc = hf1.colorbar(hIm,format=sfmt)
        hc.set_label('data numbers ' + str(data.dtype))
        hAx.set_xlabel('x-pixels')
        hAx.set_ylabel('y-pixels')

        for j,i in enumerate(rawFrameInd):
            #print('raw {}  rel {} '.format(i,j))
            #hAx.imshow(data[j,...]) #slower
            hIm.set_data(data[j,...])  # faster
            hT.set_text('RawFrame#: {} RelFrame# {}'.format(rawFrameInd[j],i) )
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

def doplotsave(bigfn,data,rawind,clim,dohist,meanImg,writeFITS,saveMat):
    outStem = splitext(expanduser(bigfn))[0]

    if dohist:
        ax=figure().gca()
        hist(data.ravel(), bins=256,log=True)
        ax.set_title('histogram of {}'.format(bigfn))
        ax.set_ylabel('frequency of occurence')
        ax.set_xlabel('data value')

    if meanImg:
        meanStack = data.mean(axis=0).astype(np.uint16) #DO NOT use dtype= here, it messes up internal calculation!
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
#%% saving
    if writeFITS:
        from astropy.io import fits
        #TODO timestamp frames
        if meanImg:
            fitsFN = outStem + '_mean_frames.fits'
            fitsData = meanStack
            print('writing MEAN image data as ' + fitsFN)
        else:
            fitsFN = outStem + '_frames.fits'
            fitsData = rawImgData
            print('writing ' + str(fitsData.dtype) + ' raw image data as ' + fitsFN)
        hdu = fits.PrimaryHDU(fitsData)
        hdu.writeto(fitsFN,clobber=True)
        print('the orientation of this FITS in NASA FV program and the preview image shown in Python should/must have the same orientation and pixel indexing')


    if saveMat:
        from scipy.io import savemat
        matFN = outStem + '_frames.mat'
        print('writing raw image data as ' + matFN)
        matdata = {'rawimgdata':rawImgData}
        savemat(matFN,matdata,oned_as='column')


if __name__ == "__main__":
    from matplotlib.pyplot import figure,show, hist, draw, pause
    from matplotlib.colors import LogNorm
    from matplotlib.ticker import ScalarFormatter
    #import matplotlib.animation as anim
    p = argparse.ArgumentParser(description='Raw .DMCdata file reader')
    p.add_argument('infile',help='.DMCdata file name and path',type=str,nargs='?',default='')
    p.add_argument('-p','--pix',help='nx ny  number of x and y pixels respectively',nargs=2,default=(512,512),type=int)
    p.add_argument('-b','--bin',help='nx ny  number of x and y binning respectively',nargs=2,default=(1,1),type=int)
    p.add_argument('-f','--frames',help='frame indices of file (not raw)',nargs=3,metavar=('start','stop','stride'), type=np.int64) #don't use string
    p.add_argument('-m','--movie',help='seconds per frame. ',type=float)
    p.add_argument('-c','--clim',help='min max   values of intensity expected (for contrast scaling)',nargs=2,type=float)
    p.add_argument('-r','--rate',help='raw frame rate of camera',type=float)
    p.add_argument('-s','--startutc',help='utc time of nights recording')
    p.add_argument('--fits',help='write a .FITS file of the data you extract',action='store_true')
    p.add_argument('--mat',help="write a .mat MATLAB data file of the extracted data",action='store_true')
    p.add_argument('--avg',help='return the average of the requested frames, as a single image',action='store_true')
    p.add_argument('--hist',help='makes a histogram of all data frames',action='store_true')
    p.add_argument('-v','--verbose',help='debugging',action='count',default=0)
    a = p.parse_args()

    rawImgData,rawInd,finf = goRead(a.infile, a.pix, a.bin,a.frames, a.rate,a.startutc,a.verbose)
#%% plots and save
    doPlayMovie(rawImgData,finf,a.movie, a.clim,rawInd)

    doplotsave(a.infile,rawImgData,rawInd,a.clim,a.hist,a.avg,a.fits,a.mat)
    show()