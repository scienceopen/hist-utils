import os.path 
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2
import struct
# local import
import rawDMCreader as rdr

#------------------------------------
def main(argv):
     #sys.argv is always strings
    nargin = len(argv)
    BigFN = os.path.expanduser(argv[1])
    BigExt = os.path.splitext(BigFN)[1]
    
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

#get params
    if (BigExt == '.DMCdata'):
        (SuperX,SuperY,Nmetadata,BytesPerFrame,PixelsPerImage,nFrame,nFrameExtract) = rdr.getDMCparam(
           BigFN,xPix,yPix,xBin,yBin,FrameInd)
        fid = open(BigFN, 'rb')
        (grayRef,rawIndRef) = rdr.getDMCframe(fid,0,BytesPerFrame,PixelsPerImage,Nmetadata,SuperX,SuperY)
        grayRef = sixteen2eight(grayRef,Clim)
    elif (BigExt == '.avi'): 
        fid = cv2.VideoCapture(BigFN)
        #print(fid.isOpened())
        nFrame = fid.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
        if all(FrameInd == 0): 
            FrameInd = np.arange(0,nFrame,1,dtype=np.uint64) # has to be numpy for > comparison
        grayRef = cv2.cvtColor(fid.read()[1], cv2.COLOR_BGR2GRAY)
    else: sys.exit('unknown file type: ' + BigExt)

    print('processing '+str(nFrame) + ' frames from ' + BigFN)

#setup figures
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)    
    cv2.namedWindow('flowHSV', cv2.WINDOW_NORMAL)
   
    for iFrm in FrameInd:
        if (BigExt == '.DMCdata'):
            (gray,rawIndGray) = rdr.getDMCframe(fid,iFrm+1,BytesPerFrame,PixelsPerImage,Nmetadata,SuperX,SuperY)
            gray = sixteen2eight(gray,Clim)
        elif (BigExt == '.avi'): 
            gray = cv2.cvtColor(fid.read()[1], cv2.COLOR_BGR2GRAY)

        flow = cv2.calcOpticalFlowFarneback(grayRef, gray, 
               pyr_scale=0.5, levels=1, winsize=3, iterations=5,
               poly_n = 3, poly_sigma=1.5,flags=1)
# plotting
        cv2.imshow('image', draw_flow(gray,flow) )
        cv2.imshow('flowHSV', draw_hsv(flow) )
        if cv2.waitKey(1) == 27: # MANDATORY FOR PLOTTING TO WORK!
            break
        grayRef = gray; #rawIndRef = rawIndGray
#------------
    if (BigExt == '.DMCdata'):
        fid.close()    
    elif (BigExt == '.avi'):
        fid.release()

    cv2.destroyAllWindows()
#-----------------------------------------------------------


def draw_flow(img, flow, step=16):
    scaleFact = 10 #arbitary factor to make flow visible
    h, w = img.shape[:2]
    y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2,-1)
    fx, fy = scaleFact * flow[y,x].T
    #create line endpoints
    lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
    lines = np.int32(lines) #+ 0.5)
    #create image and draw
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.polylines(vis, lines, 0, (0, 255, 0))
    for (x1, y1), (x2, y2) in lines:
        cv2.circle(vis, (x1, y1), 1, (0, 255, 0), -1)
    return vis

def draw_hsv(flow):
    scaleFact = 10 #arbitary factor to make flow visible
    h, w = flow.shape[:2]
    fx, fy = scaleFact*flow[:,:,0], scaleFact*flow[:,:,1]
    ang = np.arctan2(fy, fx) + np.pi
    v = np.sqrt(fx*fx+fy*fy)
    hsv = np.zeros((h, w, 3), np.uint8)
    hsv[...,0] = ang*(180/np.pi/2)
    hsv[...,1] = 255
    hsv[...,2] = np.minimum(v*4, 255)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return bgr

def warp_flow(img, flow):
    h, w = flow.shape[:2]
    flow = -flow
    flow[:,:,0] += np.arange(w)
    flow[:,:,1] += np.arange(h)[:,np.newaxis]
    res = cv2.remap(img, flow, None, cv2.INTER_LINEAR)
    return res

def sixteen2eight(I,Clim):
    minVal = Clim[0]; maxVal = Clim[1];
    I = I.astype('float32')
    #print(str(max(I.flatten())) + ' ' + str(min(I.flatten())) )
    Q = I
    Q[I > maxVal] = maxVal #clip high end
    Q[I < minVal] = minVal #boost low end
    
    Q = np.divide((Q - minVal),(maxVal - minVal)) #stretch to [0,1]
    Q = Q * 255 # stretch to [0,255]
    return Q.astype('uint8')

if __name__ == '__main__':
    sys.exit(main(sys.argv))
  



