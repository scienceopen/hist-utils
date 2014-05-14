# reads .DMCdata files and displays them
# Michael Hirsch
# GPL v3+ license
import os,sys
import numpy as np
import matplotlib.pyplot as plt
#import matplotlib.animation as anim
import matplotlib.cm as cm
import struct
#import matplotlib.image as mpimg
import cv2 #for python3 broken plt.imshow
#import warnings
### local imports
import getRawInd as gri


# Examples:
# python3 rawDMCreader.py '~/HSTdata/DataField/2013-04-14/HST1/2013-04-14T07-00-CamSer7196_frames_363000-1-369200.DMCdata' 512 512 1 1 'all' 0.01 100 4000

def main(argv):
    debug=False
     #sys.argv is always strings
    nargin = len(argv)
    BigFN = os.path.expanduser(argv[1])
    
    if nargin<3: xPix=512; yPix=512
    else: xPix = int(argv[2]); yPix = int(argv[3])
    if nargin<5: xBin = 1; yBin = 1
    else: xBin= int(argv[4]); yBin= int(argv[5])
    if nargin<7: FrameInd=[0,0]
    else: FrameInd =np.arange(int(argv[6]), int(argv[7]))
    if nargin<9: playMovie=0.01
    else: playMovie= float(argv[8])
    if nargin<10: Clim=None
    else: Clim= (float(argv[9]),float(argv[10]))
    
    if nargin<12: rawFrameRate=None
    else: rawFrameRate= float(argv[11])
    if (nargin < 13) or rawFrameRate: startUTC=None
    else: startUTC= argv[12]
# setup data parameters
    (SuperX,SuperY,Nmetadata,BytesPerFrame,PixelsPerImage,nFrame,nFrameExtract) = getDMCparam(BigFN,xPix,yPix,xBin,yBin,FrameInd)

# preallocate
    data = np.zeros((SuperY,SuperX,nFrameExtract),dtype=np.uint16)
    rawFrameInd = np.zeros((nFrameExtract,1)) #NOTE python may not require float64 like Matlab..?

    fid = open(BigFN, 'rb')

    jFrm=0 
    for iFrm in FrameInd:
        (data[:,:,jFrm],rawFrameInd[jFrm]) = getDMCframe(fid,iFrm,BytesPerFrame,PixelsPerImage,Nmetadata,SuperX,SuperY)
        jFrm += 1 #has to be here due to zero indexing 
    
    fid.close()
    
    if not (playMovie == 0):
        if sys.version_info[0] ==3:
           # from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
            #from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar
            sys.exit('Python 3 currently cannot do imshow correctly with Matlabplotlib 1.3.1')
            #warnings.warn('Python 3 Matplotlib could not plot this as of Matplotlib ver 1.3.1')
        doPlayMovie(data,SuperX,SuperY,FrameInd,playMovie,Clim,rawFrameInd)

    #ani = anim.ArtistAnimation(hFig,updatePlot, interval=250, blit=True, repeat_delay=1000)
    #plt.show()
########## END OF MAIN #######################
def getDMCparam(BigFN,xPix,yPix,xBin,yBin,FrameInd):
    SuperX = int(xPix/xBin) #for python 3
    SuperY = int(yPix/yBin)
    bpp = 16
    nHeadBytes = 4
    Nmetadata = int(nHeadBytes/2) #TODO not true for DMC2data files!
    PixelsPerImage= SuperX * SuperY
    BytesPerImage = int(PixelsPerImage*bpp/8)
    BytesPerFrame = BytesPerImage + nHeadBytes

# get file size
    if not os.path.isfile(BigFN): sys.exit('file does not exist: ' + BigFN)
    fileSizeBytes = os.path.getsize(BigFN)

    if fileSizeBytes < BytesPerImage:
        sys.exit('File size ' + str(fileSizeBytes) + 
                 ' is smaller than a single image frame!')

    nFrame = int(fileSizeBytes / BytesPerFrame)

    if nFrame%1 != 0:
        print("Looks like I am not reading this file correctly, with BPF: " + 
              str(BytesPerFrame) )


    (firstRawInd,lastRawInd) = gri.getRawInd(BigFN,BytesPerImage,nHeadBytes,Nmetadata)
    print(str(nFrame) + ' frames in file ' + BigFN)
    print('   file size in Bytes: '  +str(fileSizeBytes))
    print("first / last raw frame #'s: " + str(firstRawInd) + " / " + 
          str(lastRawInd))

# if no requested frames were specified, read all frames. Otherwise, just
# return the requested frames
    if all(FrameInd == 0): 
        FrameInd = np.arange(0,nFrame,1,dtype=np.uint64) # has to be numpy for > comparison
    badReqInd = FrameInd>nFrame
# check if we requested frames beyond what the BigFN contains
    if any(badReqInd):
        sys.exit('You have requested Frames ' + str(FrameInd[badReqInd]) +
                 ', which exceeds the length of ' + BigFN)
    nFrameExtract = len(FrameInd); #to preallocate properly

    nBytesExtract = nFrameExtract*BytesPerFrame
    print('Extracting ' + str(nFrameExtract) + ' frames, totaling ' + str(nBytesExtract) + ' bytes.')
    if nBytesExtract > 2e9:
        print('This will require ' + str(nBytesExtract/1e9) +
              ' Gigabytes of RAM. Do you have enough RAM?')
    return SuperX,SuperY,Nmetadata,BytesPerFrame,PixelsPerImage,nFrame,nFrameExtract

def getDMCframe(fid,iFrm,BytesPerFrame,PixelsPerImage,Nmetadata,SuperX,SuperY):
    #print(type(iFrm)); print(type(BytesPerFrame)); 
    currByte = int((iFrm) * BytesPerFrame) # to fix that mult casts to float64 here!

	#advance to start of frame in bytes
    fid.seek(currByte,0) #no return value
	#read data
    currFrame = np.fromfile(fid, np.uint16,PixelsPerImage).reshape((SuperY,SuperX))
    #currVect= np.fromfile(fid, np.uint16,PixelsPerImage)
    #print(str(iFrm) + ' ' + str(currVect.shape) + 
    #      'index ' + str(jFrm) )
    #data[:,:,jFrm] = currVect.reshape((SuperY,SuperX)) #helps with debugging

    rawFrameInd = getRawFrameInd(fid,Nmetadata)
    return currFrame,rawFrameInd

def getRawFrameInd(fid,Nmetadata):
    metad = np.fromfile(fid, np.uint16,Nmetadata)
    metad = struct.pack('<2H',metad[1],metad[0]) # reorder 2 uin16
    rawFrameInd = struct.unpack('<I',metad)[0]
    #print(' raw ' + str(rawFrameInd[jFrm]))
    return rawFrameInd

def doPlayMovie(data,SuperX,SuperY,FrameInd,playMovie,Clim,rawFrameInd):
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
       # print(str(iFrm) + ' ' + str(jFrm))
        hIm.set_data(data[:,:,jFrm])  #plt.imshow(currFrame)
        hT.set_text('RawFrame#: ' + str(rawFrameInd[jFrm]) + 
                'RelFrame#' + str(iFrm) )
        plt.draw()
        plt.pause(playMovie)
        jFrm += 1  #yes, at end of for loop
    plt.close()
    #hFig.canvas.draw()


if __name__ == "__main__":
    #print(sys.argv)
    sys.exit(main(sys.argv))
    
