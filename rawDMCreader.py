#!/usr/bin/env python3
# reads .DMCdata files and displays them
# Primarily tested with Python 3.4 on Linux, but should also work for Python 2.7 on any operating system.
# Michael Hirsch
# GPL v3+ license
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import pdb
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

# preallocate
    data = np.zeros((SuperY,SuperX,nFrameExtract),dtype=np.uint16)
    rawFrameInd = np.zeros((nFrameExtract,1),dtype=int)

    with open(BigFN, 'rb') as fid:
        jFrm=0
        for iFrm in FrameInd:
            data[:,:,jFrm],rawFrameInd[jFrm] = getDMCframe(fid,iFrm,BytesPerFrame,PixelsPerImage,Nmetadata,SuperX,SuperY)
            jFrm += 1


    #doPlayMovie(data,SuperX,SuperY,FrameInd,playMovie,Clim,rawFrameInd)

    if playMovie:
        hf = plt.figure(1); plt.clf()
        himg = plt.imshow(data[:,:,0],cmap='gray')
        ht = plt.title('')
        plt.colorbar()
        plt.xlabel('x')
        plt.ylabel('y')

        #blit=False so that Title updates!
        anim.FuncAnimation(hf,animate,range(nFrameExtract),fargs=(data,himg,ht), interval=playMovie, blit=False, repeat_delay=1000)
        plt.show()

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
    currByte = int((iFrm) * BytesPerFrame) # to fix that mult casts to float64 here!

	#advance to start of frame in bytes
    fid.seek(currByte,0) #no return value
	#read data
    currFrame = np.fromfile(fid, np.uint16,PixelsPerImage).reshape((SuperY,SuperX))

    rawFrameInd = getRawFrameInd(fid,Nmetadata)
    return currFrame,rawFrameInd

def getRawFrameInd(fid,Nmetadata):
    metad = np.fromfile(fid, np.uint16,Nmetadata)
    metad = struct.pack('<2H',metad[1],metad[0]) # reorder 2 uint16
    rawFrameInd = struct.unpack('<I',metad)[0]
    #print(' raw ' + str(rawFrameInd[jFrm]))
    return rawFrameInd

def doPlayMovie(data,SuperX,SuperY,FrameInd,playMovie,Clim,rawFrameInd):
  if playMovie:
    print('attemping movie playback')
    hf1 = plt.figure(1)
    hAx = hf1.add_subplot(111)
    if not Clim:
        hIm = plt.imshow(data[:,:,0], cmap = plt.get_cmap('gray') )
    else:
        hIm = plt.imshow(data[:,:,0],
                        vmin=Clim[0],vmax=Clim[1],
                        cmap = plt.get_cmap('gray') )
    hT = hAx.text(0.5,1.005,'', transform=hAx.transAxes)
    hf1.colorbar(hIm)
    hAx.set_xlabel('x-pixels')
    hAx.set_ylabel('y-pixels')

    jFrm = 0
    for iFrm in FrameInd:
        print(str(iFrm) + ' ' + str(jFrm))
        plt.imshow(data[:,:,jFrm])
        #hIm.set_data(data[:,:,jFrm])  #
        hT.set_text('RawFrame#: ' + str(rawFrameInd[jFrm]) +
                'RelFrame#' + str(iFrm) )
        plt.show(True)
        plt.pause(playMovie)
        jFrm += 1  #yes, at end of for loop
    plt.close()
  else:
    print('skipped movie playback')
    #hFig.canvas.draw()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description='Raw .DMCdata file reader')
    p.add_argument('-i','--in',help='.DMCdata file name and path',required=True)
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
    args = vars(p.parse_args())

    BigFN = os.path.expanduser(args['in'])
    xyPix = args['pix']
    xyBin = args['bin']
    FrameInd = args['frames']
    playMovie = args['movie']
    Clim = args['clim']
    rawFrameRate = args['rate']
    if rawFrameRate: print('raw frame rate timing not yet implemented')
    startUTC = args['startutc']
    if startUTC: print('frame UTC timing not yet implemented')
    writeFITS = args['fits']
    saveMat = args['mat']
    meanImg = args['avg']


    rawImgData = goRead(BigFN,xyPix,xyBin,FrameInd,playMovie,Clim,rawFrameRate,startUTC,verbose=0)
    if meanImg:
        meanStack = np.mean(rawImgData,axis=2).astype(np.uint16) #DO NOT use dtype= here, it messes up internal calculation!
#        plt.figure(32);plt.clf()
#        plt.imshow(meanStack,cmap='gray')
#        plt.xlabel('x')
#        plt.ylabel('y')
#        plt.title('mean of image frames')
#        plt.colorbar()
#        plt.show()
   # pdb.set_trace()


    outStem = os.path.splitext(BigFN)[0]
    if writeFITS:
        from astropy.io import fits
        #TODO timestamp frames
        if meanImg:
            fitsFN = outStem + '_mean_frames.fits'
            fitsData = meanStack
            print('writing MEAN image data as ' + fitsFN)
        else:
            fitsFN = outStem + '_frames.fits'
            fitsData = np.transpose(rawImgData,axes=[2,0,1])
            print('writing raw image data as ' + fitsFN)
        #pdb.set_trace()
        hdu = fits.PrimaryHDU(fitsData)
        hdulist = fits.HDUList([hdu])
        hdulist.writeto(fitsFN,clobber=True)

    if saveMat:
        from scipy.io import savemat
        matFN = outStem + '_frames.mat'
        print('writing raw image data as ' + matFN)
        matdata = {'rawimgdata':rawImgData}
        savemat(matFN,matdata,oned_as='column')

