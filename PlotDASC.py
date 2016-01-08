#!/usr/bin/env python3
"""
Plots / plays Poker Flat DASC all-sky camera data FITS files

"""
from histutils.readDASCfits import readCalFITS

if __name__ == '__main__':
    from scipy.misc import bytescale

    from argparse import ArgumentParser
    p = ArgumentParser(description='for Poker Flat DASC all sky camera, read az/el mapping and images')
    p.add_argument('indir',help='directory of .fits or specific .fits file')
    p.add_argument('-a','--azfn',help='filename for DASC .fits azimuth calibration')
    p.add_argument('-e','--elfn',help='filename for DASC .fits elevation calibration')
    p=p.parse_args()


    data,coordnames,dataloc,sensorloc,times  = readCalFITS(p.indir,p.azfn,p.elfn)
    img = data['image']

    try:
        az = dataloc[:,1].reshape(img.shape[1:])
        el = dataloc[:,2].reshape(img.shape[1:])
    except Exception:
        pass

    img8 = bytescale(img,0,1000)
#%% play movie
    try:
        import cv2 # easy way to show fast movie

        for I in img8:
            cv2.imshow('DASC',I)
            cv2.waitKey(500)
        cv2.destroyAllWindows()
    except Exception:
        pass