import logging
from matplotlib.pyplot import figure,draw,subplots
#from matplotlib.colors import LogNorm
from datetime import datetime
from pytz import UTC
try:
    from GeoData.utilityfuncs import readAllskyFITS
except ImportError:
    GeoData=None
#
from gridaurora.plots import writeplots

dpi = 100

def plotPlainImg(sim,cam,rawdata,t,makeplot,figh,odir):
    """
    No subplots, just a plan

    http://stackoverflow.com/questions/22408237/named-colors-in-matplotlib
    """
    for R,C in zip(rawdata,cam):
        figure(figh).clf()
        fg = figure(figh)
        ax = fg.gca()
        ax.set_axis_off()
        ax.imshow(R[t,:,:],
                  origin='lower',
                  vmin=max(C.clim[0],1), vmax=C.clim[1],
                  cmap='gray')
        ax.text(0.05, 0.075, datetime.fromtimestamp(C.tKeo[t],tz=UTC).strftime('%Y-%m-%dT%H:%M:%S.%f')[:23],
                     ha='left',
                     va='top',
                     transform=ax.transAxes,
                     color='limegreen',
                     #weight='bold',
                     size=24
                    )

        draw() #Must have this here or plot doesn't update in animation multiplot mode!
        if 'png' in makeplot:
            writeplots(fg,'cam{}rawFrame'.format(C.name),t,odir)

#%%
def plotRealImg(sim,cam,rawdata,t,makeplot,odir=None,asi=None):
    """
    sim: histfeas/simclass.py
    cam: histfeas/camclass.py
    t:
    makeplot: list/tuple of requested plots
    odir: output directory (where to write results)
    asi: filename of allsky camera

    plots both cameras together,
    and magnetic zenith 1-D cut line
    and 1 degree radar beam red circle centered on magnetic zenith
    """
    T=[None,None]

    ncols=3 if asi is not None else 2

    fg,axs = subplots(nrows=1,ncols=ncols, figsize=(15,12),dpi=dpi)
    #fg.set_size_inches(15,5) #clips off
    #for i,(R,C,ax) in enumerate(zip(rawdata,cam,axm)):
    for i in range(ncols):
        #FIXME this would need help if one of the cameras isn't plotted (this will probably never happen)
        if i<3:
            dtframe = updateframe(t,rawdata[i],cam[i],axs[i],fg)
            T[i] = dtframe #hold times for all cameras at this time step

    draw() #Must have this here or plot doesn't update in animation multiplot mode!

    if 'png' in makeplot:
        writeplots(fg,'rawFrame',T[0],makeplot,odir) #FIXME: T[0] is fastest cam now, but needs generalization


def updateframe(t,raw,cam,ax,fg):
    showcb = False

    if raw.ndim ==3:
        frame = raw[t,...]
    elif raw.ndim==2:
        frame = raw
    else:
        raise ValueError('ndim==3 or 2')
    #plotting raw uint16 data
    hi = ax.imshow(frame,
                     origin='lower',interpolation='none',
                     #aspect='equal',
                     #extent=(0,C.superx,0,C.supery),
                     vmin=max(cam.clim[0],1), vmax=cam.clim[1],
                     cmap='gray',)
                     #norm=LogNorm())
    ax.autoscale(False) # False for case where we put plots on top of image

    if showcb: #showing the colorbar makes the plotting go 5-10x more slowly
        hc = fg.colorbar(hi, ax=ax) #not cax!
        hc.set_label('{} data numbers'.format(raw.dtype))

    dtframe = datetime.utcfromtimestamp(cam.tKeo[t])

    ax.set_title('Cam{}: {}'.format(cam.name,dtframe))

    #ax.set_xlabel('x-pixel')
    #if cam.name==0:
    #    ax.set_ylabel('y-pixel')
#%% plotting 1D cut line
    try:
       ax.plot(cam.cutcol,cam.cutrow,
             marker='.',linestyle='none',color='blue',markersize=1)
        #plot magnetic zenith
       ax.scatter(x=cam.cutcol[cam.angleMagzenind],
               y=cam.cutrow[cam.angleMagzenind],
               marker='o',facecolors='none',color='red',s=500)
    except Exception:
       logging.debug('skipped plotting cut line on video ind {}'.format(t))
#%% plot cleanup
    ax.grid(False) #in case Seaborn is used
    return dtframe