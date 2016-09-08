#!/usr/bin/env python
from . import Path
from numpy import uint16
from datetime import datetime
from pytz import UTC
try:
    import simplekml as skml
except ImportError:
    skml = None
#
from mpl_toolkits.mplot3d import Axes3D #needed for this file
from matplotlib.pyplot import figure, hist, draw, pause
from matplotlib.colors import LogNorm
#from matplotlib.ticker import ScalarFormatter
#import matplotlib.animation as anim
#
from pymap3d.coordconv3d import ecef2geodetic

def doPlayMovie(data,playMovie,ut1_unix=None,rawFrameInd=None,clim=None):
    if not playMovie or data is None:
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
    if bigfn is None or data is None:
        return

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


def animate(i,data,himg,ht):
    #himg = plt.imshow(data[:,:,i]) #slow, use set_data instead
    himg.set_data(data[i,:,:])
    ht.set_text('RelFrame#' + str(i) )
    #'RawFrame#: ' + str(rawFrameInd[jFrm]) +

    draw() #plot won't update without plt.draw()!
    #plt.pause(0.01)
    #plt.show(False) #breaks (won't play)
    return himg,ht

def plotLOSecef(cam,odir):

    fg = figure()
    clr = ['b','r','g','m']

    if odir and skml is not None:
        kml1d = skml.Kml()

    for C in cam:
        if not C.usecam:
            continue

        ax = fg.gca(projection='3d')
        ax.plot(xs=C.x2mz, ys=C.y2mz, zs=C.z2mz, zdir='z',
                    color=clr[C.name], label=str(C.name))
        ax.set_title('LOS to magnetic zenith')

        if odir and skml is not None: #Write KML
            #convert LOS ECEF -> LLA
            loslat,loslon,losalt = ecef2geodetic(C.x2mz, C.y2mz, C.z2mz)
            kclr = ['ff5c5ccd','ffff0000']
            #camera location points
            bpnt = kml1d.newpoint(name='HST {}'.format(C.name),
                                  description='camera {} location'.format(C.name),
                                  coords=[(C.lon, C.lat)])
            bpnt.altitudemode = skml.AltitudeMode.clamptoground
            bpnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/pink-blank.png'
            bpnt.style.iconstyle.scale = 2.0
            #show cam to mag zenith los
            linestr = kml1d.newlinestring(name='')
            #TODO this is only first and last point without middle!
            linestr.coords = [(loslon[0],   loslat[0],  losalt[0]),
                              (loslon[-1], loslat[-1], losalt[-1])]
            linestr.altitudemode = skml.AltitudeMode.relativetoground
            linestr.style.linestyle.color = kclr[C.name]


    ax.legend()
    if odir and skml is not None:
        kmlfn = odir / 'debug1dcut.kmz'
        print('saving {}'.format(kmlfn))
        kml1d.savekmz(str(kmlfn))

def plotnear_rc(R,C,name,shape):

    clr = ['b','r','g','m']
    ax = figure().gca()
    ax.plot(C, R,
            color=clr[name],
            label='cam{} preLSQ'.format(name),
            linestyle='None',marker='.')
    ax.legend()
    ax.set_xlabel('x'); ax.set_ylabel('y')
    #ax.set_title('pixel indices (pre-least squares)')
    ax.set_xlim([0, shape[1]])
    ax.set_ylim([0, shape[0]])