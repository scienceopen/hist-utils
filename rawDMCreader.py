#!/usr/bin/env python3
# reads .DMCdata files and displays them
# Primarily tested with Python 3.4 on Linux, but should also work for Python 2.7 on any operating system.
# requires astropy if you want to write FITS
# Michael Hirsch
# GPL v3+ license
from __future__ import division
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.ticker import ScalarFormatter
#import matplotlib.animation as anim
#import pdb
import argparse
import struct
import warnings
### local imports
import getRawInd as gri


# Examples:
# python3 rawDMCreader.py '~/HSTdata/DataField/2013-04-14/HST1/2013-04-14T07-00-CamSer7196_frames_363000-1-369200.DMCdata' 512 512 1 1 'all' 0.01 100 4000

def goRead(BigFN,xyPix,xyBin,FrameInd,playMovie=None,Clim=None,rawFrameRate=None,startUTC=None,verbose=0):

    # setup data parameters
    SuperX,SuperY,Nmetadata,BytesPerFrame,PixelsPerImage,nFrame,nFrameExtract,FrameInd = getDMCparam(BigFN,xyPix,xyBin,FrameInd,verbose)

# preallocate *** LABVIEW USES ROW-MAJOR ORDERING C ORDER
    data = np.zeros((nFrameExtract,SuperY,SuperX),dtype=np.uint16,order='C')
    rawFrameInd = np.zeros(nFrameExtract,dtype=int)

    with open(BigFN, 'rb') as fid:
        jFrm=0
        for iFrm in FrameInd:
            data[jFrm,:,:],rawFrameInd[jFrm] = getDMCframe(fid,iFrm,BytesPerFrame,PixelsPerImage,Nmetadata,SuperX,SuperY)
            jFrm += 1

    #more reliable if slower playback
    doPlayMovie(data,SuperX,SuperY,FrameInd,playMovie,Clim,rawFrameInd)

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
    himg.set_data(data[:,:,i])
    ht.set_text('RelFrame#' + str(i) )
    #'RawFrame#: ' + str(rawFrameInd[jFrm]) +

    plt.draw() #plot won't update without plt.draw()!
    #plt.show(False) #breaks (won't play)
    return himg,ht

def getDMCparam(BigFN,xyPix,xyBin,FrameInd,verbose=0):
    SuperX = xyPix[0] // xyBin[0] # "//" keeps as integer
    SuperY = xyPix[1] // xyBin[1]

    bpp = 16
    nHeadBytes = 4
    Nmetadata = nHeadBytes//2 #TODO not true for DMC2data files!
    PixelsPerImage= SuperX * SuperY
    BytesPerImage = PixelsPerImage*bpp//8
    BytesPerFrame = BytesPerImage + nHeadBytes

# get file size
    fileSizeBytes = os.path.getsize(BigFN)

    if fileSizeBytes < BytesPerImage:
        raise RuntimeError('File size ' + str(fileSizeBytes) +
                 ' is smaller than a single image frame!')

    nFrame = fileSizeBytes / BytesPerFrame #for quick check diagnostic, left as float temporarily

    if nFrame%1 != 0:
        warnings.warn("Looks like I am not reading this file correctly, with BPF: " +
              str(BytesPerFrame) )
    nFrame = int(nFrame) # this is a nice quick check diagnostic above


    (firstRawInd,lastRawInd) = gri.getRawInd(BigFN,BytesPerImage,nHeadBytes,Nmetadata)
    if verbose >=0:
        print(str(nFrame) + ' frames in file ' + BigFN)
        print('   file size in Bytes: '  +str(fileSizeBytes))
        print("first / last raw frame #'s: " + str(firstRawInd) + " / " +
          str(lastRawInd))

# setup frame indices
# if no requested frames were specified, read all frames. Otherwise, just
# return the requested frames
    if FrameInd is None:
        FrameInd = np.arange(nFrame,dtype=int) # has to be numpy for > comparison
        if verbose>=0:
            print('automatically selected all frames in file')
    elif isinstance(FrameInd,int):
        FrameInd =np.arange(FrameInd,dtype=int)
    elif len(FrameInd) == 3:
        FrameInd =np.arange(FrameInd[0],FrameInd[1],FrameInd[2],dtype=int)



    badReqInd = FrameInd>nFrame
# check if we requested frames beyond what the BigFN contains
    if np.any(badReqInd):
        raise RuntimeError('You have requested Frames ' + str(FrameInd[badReqInd]) +
                 ', which exceeds the length of ' + BigFN)
    nFrameExtract = len(FrameInd) #to preallocate properly

    nBytesExtract = nFrameExtract*BytesPerFrame
    if verbose >= 0:
        print(BigFN + ' contains ' + str(nFrameExtract) + ' frames, totaling ' + str(nBytesExtract) + ' bytes.')
    if nBytesExtract > 4e9:
        warnings.warn('This will require ' + str(nBytesExtract/1e9) + ' Gigabytes of RAM.')
    return SuperX,SuperY,Nmetadata,BytesPerFrame,PixelsPerImage,nFrame,nFrameExtract,FrameInd

def getDMCframe(fid,iFrm,BytesPerFrame,PixelsPerImage,Nmetadata,SuperX,SuperY,verbose=0):
    #print(type(iFrm)); print(type(BytesPerFrame));
    currByte = int(iFrm * BytesPerFrame) # to fix that mult casts to float64 here!

	#advance to start of frame in bytes
    fid.seek(currByte,0) #no return value
	#read data ***LABVIEW USES ROW-MAJOR C ORDERING!!
    currFrame = np.fromfile(fid, np.uint16,PixelsPerImage).reshape((SuperY,SuperX),order='C')

    rawFrameInd = getRawFrameInd(fid,Nmetadata)
    return currFrame,rawFrameInd

def getRawFrameInd(fid,Nmetadata):
    metad = np.fromfile(fid, np.uint16,Nmetadata)
    metad = struct.pack('<2H',metad[1],metad[0]) # reorder 2 uint16
    rawFrameInd = struct.unpack('<I',metad)[0]
    #print(' raw ' + str(rawFrameInd[jFrm]))
    return rawFrameInd

def doPlayMovie(data,SuperX,SuperY,FrameInd,playMovie,Clim,rawFrameInd):
  if playMovie is not None:
    sfmt = ScalarFormatter(useMathText=True)
    print('attemping movie playback')
    hf1 = plt.figure(1)
    hAx = hf1.add_subplot(111)
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
        plt.draw()
        plt.pause(playMovie)
        jFrm += 1  #yes, at end of for loop
    plt.close()
  else:
    print('skipped movie playback')



if __name__ == "__main__":
    p = argparse.ArgumentParser(description='Raw .DMCdata file reader')
    p.add_argument('-i','--infile',help='.DMCdata file name and path',required=True)
    p.add_argument('-p','--pix',help='nx ny  number of x and y pixels respectively',nargs=2,default=(512,512),type=int)
    p.add_argument('-b','--bin',help='nx ny  number of x and y binning respectively',nargs=2,default=(1,1),type=int)
    p.add_argument('-f','--frames',help='frame indices of file (not raw)',nargs=3,metavar=('start','stop','stride'),default=None,type=int)
    p.add_argument('-m','--movie',help='seconds per frame. ',default=None,type=float)
    p.add_argument('-c','--clim',help='min max   values of intensity expected (for contrast scaling)',nargs=2,default=None,type=float)
    p.add_argument('-r','--rate',help='raw frame rate of camera',default=None,type=float)
    p.add_argument('-s','--startutc',help='utc time of nights recording',default=None)
    p.add_argument('--fits',help='write a .FITS file of the data you extract',action='store_true')
    p.add_argument('--mat',help="write a .mat MATLAB data file of the extracted data",action='store_true')
    p.add_argument('--avg',help='return the average of the requested frames, as a single image',action='store_true')
    p.add_argument('--png',help='writes a .png of the data you extract (currently only for --avg))',action='store_true')
    args = p.parse_args()

    BigFN = os.path.expanduser(args.infile)
    xyPix = args.pix
    xyBin = args.bin
    FrameInd = args.frames
    playMovie = args.movie
    Clim = args.clim
    rawFrameRate = args.rate
    if rawFrameRate: print('raw frame rate timing not yet implemented')
    startUTC = args.startutc
    if startUTC: print('frame UTC timing not yet implemented')
    writeFITS = args.fits
    saveMat = args.mat
    meanImg = args.avg


    rawImgData = goRead(BigFN,xyPix,xyBin,FrameInd,playMovie,Clim,rawFrameRate,startUTC,verbose=0)
    outStem = os.path.splitext(BigFN)[0]

    if meanImg:
        meanStack = np.mean(rawImgData,axis=0).astype(np.uint16) #DO NOT use dtype= here, it messes up internal calculation!
        #if playMovie is not None:
        plt.figure(32)
        ax = plt.axes()
        if Clim is None:
            ax.imshow(meanStack,cmap='gray',origin='lower',norm=LogNorm())
        else:
            ax.imshow(meanStack,cmap='gray',origin='lower', vmin=Clim[0], vmax=Clim[1],norm=LogNorm())
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('mean of image frames')
        #plt.colorbar()
        if args.png:
            pngfn = outStem + '.png'
            print('writing mean PNG ' + pngfn)
            plt.savefig(pngfn,dpi=150,bbox_inches='tight')
        plt.show()


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
