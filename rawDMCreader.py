#!/usr/bin/env python3
"""
reads .DMCdata files and displays them
 Primarily tested with Python 3.4 on Linux, but should also work for Python 2.7 on any operating system.
 requires astropy if you want to write FITS
 Michael Hirsch
 GPL v3+ license

NOTE: Observe the dtype=np.int64, this is for Windows Python, that wants to default to int32 instead of int64 like everyone else!
    --- we can't use long, because that's only for Python 2.7
 """
from __future__ import division, print_function
from os.path import getsize, expanduser, splitext, isfile
import numpy as np
import argparse
### local imports
import getRawInd as gri

bpp = 16
nHeadBytes = 4
# Examples:
# python3 rawDMCreader.py '~/HSTdata/DataField/2013-04-14/HST1/2013-04-14T07-00-CamSer7196_frames_363000-1-369200.DMCdata' 512 512 1 1 'all' 0.01 100 4000

def goRead(BigFN,xyPix,xyBin,FrameIndReq,playMovie=None,Clim=None,
                                    rawFrameRate=None,startUTC=None,verbose=0):

    # setup data parameters
    finf = getDMCparam(BigFN,xyPix,xyBin,FrameIndReq,verbose)

# preallocate *** LABVIEW USES ROW-MAJOR ORDERING C ORDER
    data = np.zeros((finf['nframeextract'],finf['supery'],finf['superx']),
                    dtype=np.uint16, order='C')
    rawFrameInd = np.zeros(finf['nframeextract'], dtype=np.int64)

    with open(BigFN, 'rb') as fid:
        jFrm=0
        for iFrm in finf['frameind']:
            data[jFrm,:,:], rawFrameInd[jFrm] = getDMCframe(fid,iFrm,finf,verbose)
            jFrm += 1

    #more reliable if slower playback
    doPlayMovie(data,finf,playMovie,Clim,rawFrameInd)

# on some systems, just freezes at first frame
#    if playMovie:
#        print('attempting animation')
#        hf = plt.figure(1)
#        ax = plt.axes()
#        himg = ax.imshow(data[:,:,0],cmap='gray')
#        ht = ax.set_title('')
#        plt.colorbar(himg)
#        ax.set_xlabel('x')
#        ax.set_ylabel('y')
#
#        #blit=False so that Title updates!
#        anim.FuncAnimation(hf,animate,range(nFrameExtract),fargs=(data,himg,ht), interval=playMovie, blit=False, repeat_delay=1000)
#        plt.show()

    return data
########## END OF MAIN #######################

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
        print('*** getDMCparam: {:s} is not a file!'.format(bigfn))
        return None

    #np.int64() in case we are fed a float of int
    SuperX = np.int64(xyPix[0]) // np.int64(xyBin[0]) # "//" keeps as integer
    SuperY = np.int64(xyPix[1]) // np.int64(xyBin[1])

    Nmetadata = nHeadBytes//2 #FIXME for DMCdata version 1 only
    PixelsPerImage= SuperX * SuperY
    BytesPerImage = PixelsPerImage*bpp//8
    BytesPerFrame = BytesPerImage + nHeadBytes

# get file size
    fileSizeBytes = getsize(bigfn)

    if fileSizeBytes < BytesPerImage:
        print('*** getDMCparam: File size {:d} is smaller than a single image frame!'.format(
               fileSizeBytes))
        return None


    if fileSizeBytes % BytesPerFrame:
        print("** getDMCparam: Looks like I am not reading this file correctly, with BPF: {:d}".format(
              BytesPerFrame))

    nFrame = fileSizeBytes // BytesPerFrame

    (firstRawInd,lastRawInd) = gri.getRawInd(bigfn,BytesPerImage,nHeadBytes,Nmetadata)
    if verbose > 0:
        print('{:d} frames in file {:s}'.format(nFrame,bigfn))
        print('   file size in Bytes: {:d}'.format(fileSizeBytes))
        print("first / last raw frame #'s: {:d}  / {:d} ".format(firstRawInd,lastRawInd))

# setup frame indices
# if no requested frames were specified, read all frames. Otherwise, just
# return the requested frames
    #note these assignments have to be "long", not just python "int", because on windows python 2.7 64-bit on files >2.1GB, the bytes will wrap
    if FrameIndReq is None:
        FrameInd = np.arange(nFrame,dtype=np.int64) # has to be numpy.arange for > comparison
        if verbose>0:
            print('automatically selected all frames in file')
    elif isinstance(FrameIndReq,int): #the user is specifying a step size
        FrameInd =np.arange(0,nFrame,FrameIndReq,dtype=np.int64)
    elif len(FrameIndReq) == 3:
        FrameInd =np.arange(FrameIndReq[0],FrameIndReq[1],FrameIndReq[2],dtype=np.int64)
    else:
        exit('*** getDMCparam: I dont understand your frame request')

    badReqInd = FrameInd>nFrame
# check if we requested frames beyond what the BigFN contains
    if badReqInd.any():
        exit('*** You have requested Frames ' + str(FrameInd[badReqInd]) +
                 ', which exceeds the length of {:s}'.format(bigfn))
    nFrameExtract = FrameInd.size #to preallocate properly

    nBytesExtract = nFrameExtract * BytesPerFrame
    if verbose > 0:
        print('Extracted {:d} frames from {:s} totaling {:d} bytes.'.format(
                   nFrameExtract,bigfn,nBytesExtract))
    if nBytesExtract > 4e9:
        print('** This will require {:0.2f} Gigabytes of RAM.'.format(nBytesExtract/1e9))

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
        print('*** getDMCframe: I couldnt seek to byte {:d}'.format(currByte))
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
        print('*** we may have read past end of file?')
        print(str(e))
        return None,None

    rawFrameInd = gri.meta2rawInd(f,finf['nmetadata'])
    return currFrame,rawFrameInd

def doPlayMovie(data,finf,playMovie,Clim,rawFrameInd):
  if playMovie is not None:
    sfmt = ScalarFormatter(useMathText=True)
    print('attemping movie playback')
    hf1 = figure(1)
    hAx = hf1.gca()
    if Clim is None:
        hIm = hAx.imshow(data[0,:,:], cmap = 'gray', origin='lower',norm=LogNorm() )
    else:
        hIm = hAx.imshow(data[0,:,:],
                        vmin=Clim[0],vmax=Clim[1],
                        cmap = 'gray', origin='lower', norm=LogNorm())
    hT = hAx.text(0.5,1.005,'', transform=hAx.transAxes)
    hc = hf1.colorbar(hIm,format=sfmt)
    hc.set_label('data numbers ' + str(data.dtype))
    hAx.set_xlabel('x-pixels')
    hAx.set_ylabel('y-pixels')

    jFrm = 0
    for iFrm in FrameInd:
        #print(str(iFrm) + ' ' + str(jFrm))
        #hAx.imshow(data[:,:,jFrm]) #slower
        hIm.set_data(data[jFrm,:,:])  # faster
        hT.set_text('RawFrame#: ' + str(rawFrameInd[jFrm]) +
                'RelFrame#' + str(iFrm) )
        draw()
        pause(playMovie)
        jFrm += 1  #yes, at end of for loop
    close()
  else:
    print('skipped movie playback')



if __name__ == "__main__":
    from matplotlib.pyplot import figure,show, hist, draw, pause, close
    from matplotlib.colors import LogNorm
    from matplotlib.ticker import ScalarFormatter
    #import matplotlib.animation as anim
    p = argparse.ArgumentParser(description='Raw .DMCdata file reader')
    p.add_argument('infile',help='.DMCdata file name and path',type=str,nargs='?',default='')
    p.add_argument('-p','--pix',help='nx ny  number of x and y pixels respectively',nargs=2,default=(512,512),type=int)
    p.add_argument('-b','--bin',help='nx ny  number of x and y binning respectively',nargs=2,default=(1,1),type=int)
    p.add_argument('-f','--frames',help='frame indices of file (not raw)',nargs=3,metavar=('start','stop','stride'),default=None, type=np.int64) #don't use string
    p.add_argument('-m','--movie',help='seconds per frame. ',default=None,type=float)
    p.add_argument('-c','--clim',help='min max   values of intensity expected (for contrast scaling)',nargs=2,default=None,type=float)
    p.add_argument('-r','--rate',help='raw frame rate of camera',default=None,type=float)
    p.add_argument('-s','--startutc',help='utc time of nights recording',default=None)
    p.add_argument('--fits',help='write a .FITS file of the data you extract',action='store_true')
    p.add_argument('--mat',help="write a .mat MATLAB data file of the extracted data",action='store_true')
    p.add_argument('--avg',help='return the average of the requested frames, as a single image',action='store_true')
    p.add_argument('--png',help='writes a .png of the data you extract (currently only for --avg))',action='store_true')
    p.add_argument('--hist',help='makes a histogram of all data frames',action='store_true')
    a = p.parse_args()

    BigFN = expanduser(a.infile)
    xyPix = a.pix
    xyBin = a.bin
    FrameInd = a.frames
    playMovie = a.movie
    Clim = a.clim
    rawFrameRate = a.rate
    if rawFrameRate:
        print('raw frame rate timing not yet implemented')

    startUTC = a.startutc
    if startUTC:
        print('frame UTC timing not yet implemented')

    writeFITS = a.fits
    saveMat = a.mat
    meanImg = a.avg


    rawImgData = goRead(BigFN,xyPix,xyBin,FrameInd,playMovie,Clim,rawFrameRate,startUTC,verbose=0)
    outStem = splitext(BigFN)[0]

    if a.hist:
        hist(rawImgData.ravel(), bins=256)
        show()

    if meanImg:
        meanStack = np.mean(rawImgData,axis=0).astype(np.uint16) #DO NOT use dtype= here, it messes up internal calculation!
        #if playMovie is not None:
        fg = figure(32)
        ax = fg.gca()
        if Clim is None:
            ax.imshow(meanStack,cmap='gray',origin='lower',norm=LogNorm())
        else:
            ax.imshow(meanStack,cmap='gray',origin='lower', vmin=Clim[0], vmax=Clim[1],norm=LogNorm())
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('mean of image frames')
        #plt.colorbar()
        if a.png:
            pngfn = outStem + '.png'
            print('writing mean PNG ' + pngfn)
            fg.savefig(pngfn,dpi=150,bbox_inches='tight')
        show()


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
