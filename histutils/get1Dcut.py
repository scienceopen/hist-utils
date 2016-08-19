from __future__ import division,absolute_import
from numpy import logspace
import h5py
from matplotlib.pyplot import figure
from mpl_toolkits.mplot3d import Axes3D #needed for this file
#
from pymap3d.coordconv3d import ecef2aer, ecef2geodetic

def get1Dcut(cam,odir,verbose):
    discardEdgepix = True #gets rid of duplicates beyond FOV of image that cause lsq estimation error
#%% determine slant range between other camera and magnetic zenith to evaluate at
    srpts = logspace(4.3,6.9,25) #4.5 had zero discards for hst0 #6.8 didn't quite get to zenith
#%% (0) load az/el data from Astrometry.net
    for C in cam:
        if C.usecam:
            with h5py.File(str(C.cal1Dfn),'r',libver='latest') as f:
                # NEED .value in case no modifications do in .doorient()
                C.doorient(f['/az'].value, f['/el'].value,
                           f['/ra'].value, f['/dec'].value)
            C.toecef(srpts)

    #optional: plot ECEF of points between each camera and magnetic zenith (lying at az,el relative to each camera)
    plotLOSecef(cam,odir,verbose)
#%% (2) get az,el of these points from camera to the other camera's points
    cam[0].az2pts,cam[0].el2pts,cam[0].r2pts = ecef2aer(cam[1].x2mz, cam[1].y2mz, cam[1].z2mz,
                                                             cam[0].lat, cam[0].lon, cam[0].alt_m)
    cam[1].az2pts,cam[1].el2pts,cam[1].r2pts = ecef2aer(cam[0].x2mz, cam[0].y2mz, cam[0].z2mz,
                                                             cam[1].lat, cam[1].lon, cam[1].alt_m)
#%% (3) find indices corresponding to these az,el in each image
        # and Least squares fit line to nearest points found in step 3
    for C in cam:
        if C.usecam:
            C.findClosestAzel(discardEdgepix)

#%%
    if verbose>2 and odir:
        dbgfn = odir / 'debugLSQ.h5'
        print('writing', dbgfn)
        with h5py.File(str(dbgfn),'w',libver='latest') as fid:
            for C in cam:
                fid.create_dataset('/cam{}/cutrow'.format(C.name), data= C.cutrow)
                fid.create_dataset('/cam{}/cutcol'.format(C.name), data= C.cutcol)
                fid.create_dataset('/cam{}/xpix'.format(C.name),   data= C.xpix)
    return cam

def plotLOSecef(cam,odir,verbose):
    if verbose<=0:
        return

    figecef = figure()
    clr = ['b','r','g','m']
    if verbose>1:
        import simplekml as skml
        kml1d = skml.Kml()


    for c in cam:
        axecef = figecef.gca(projection='3d')
        axecef.plot(xs=cam[c].x2mz, ys=cam[c].y2mz, zs=cam[c].z2mz, zdir='z',
                    color=clr[int(c)], label=c)
        axecef.set_title('LOS to magnetic zenith')

        if verbose and odir: #Write KML
            #convert LOS ECEF -> LLA
            loslat,loslon,losalt = ecef2geodetic(cam[c].x2mz,cam[c].y2mz,cam[c].z2mz)
            kclr = ['ff5c5ccd','ffff0000']
            #camera location points
            bpnt = kml1d.newpoint(name='HST'+c, description='camera ' +c + ' location',
                     coords=[(cam[c].lon,cam[c].lat)])
            bpnt.altitudemode = skml.AltitudeMode.clamptoground
            bpnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/pink-blank.png'
            bpnt.style.iconstyle.scale = 2.0
            #show cam to mag zenith los
            linestr = kml1d.newlinestring(name='')
            #TODO this is only first and last point without middle!
            linestr.coords = [(loslon[0],   loslat[0],  losalt[0]),
                              (loslon[-1], loslat[-1], losalt[-1])]
            linestr.altitudemode = skml.AltitudeMode.relativetoground
            linestr.style.linestyle.color = kclr[int(c)]


    axecef.legend()
    if verbose and odir:
        kmlfn = str(odir/'debug1dcut.kmz')
        print('saving {}'.format(kmlfn))
        kml1d.savekmz(kmlfn)


#
#def findClosestAzel(cam, discardEdgepix,dbglvl):
#    for c in cam:
#        azImg,elImg,azVec,elVec = cam[c].az, cam[c].el, cam[c].az2pts,cam[c].el2pts,
#
#        ny,nx = cam[c].ypix, cam[c].xpix
#
#        assert azImg.shape ==  elImg.shape
#        assert azVec.shape == elVec.shape
#        assert azImg.ndim == 2
#
#        npts = azVec.size  #numel
#        nearRow = empty(npts,dtype=int)
#        nearCol = empty(npts,dtype=int)
#        for ipt in range(npts):
#            #we do this point by point because we need to know the closest pixel for each point
#            errdist = absolute( hypot(azImg - azVec[ipt],
#                                       elImg - elVec[ipt]) )
#
## ********************************************
## THIS UNRAVEL_INDEX MUST BE ORDER = 'C'
#            nearRow[ipt],nearCol[ipt] = unravel_index(errdist.argmin(),(ny,nx),order='C')
##************************************************
#
#
#        if discardEdgepix:
#            edgeind = where(logical_or(logical_or(nearCol==0,nearCol == nx-1),
#                               logical_or(nearRow==0,nearRow==ny-1)) )[0]
#            nearRow = delete(nearRow,edgeind)
#            nearCol = delete(nearCol,edgeind)
#            if dbglvl>0: print('deleted',edgeind.size, 'edge pixels ')
#
#        cam[c].findLSQ(nearRow, nearCol)
#
#        if dbglvl>0:
#            clr = ['b','r','g','m']
#            ax = figure().gca()
#            ax.plot(nearCol,nearRow,color=clr[int(c)],label='cam'+c+'preLSQ',
#                    linestyle='None',marker='.')
#            ax.legend()
#            ax.set_xlabel('x'); ax.set_ylabel('y')
#            #ax.set_title('pixel indices (pre-least squares)')
#            ax.set_xlim([0,cam[c].az.shape[1]])
#            ax.set_ylim([0,cam[c].az.shape[0]])
#
#    return cam