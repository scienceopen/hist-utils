#!/usr/bin/env python3
from numpy import sqrt
from matplotlib.pyplot import figure,draw,subplots,close
#from matplotlib.colors import LogNorm
from datetime import datetime
from pytz import UTC
from histfeas.nans import nans
#
from dascutils.readDASCfits import readDASC
from gridaurora.plots import writeplots
from themisasi.plots import overlayrowcol

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
        ax.set_axis_off() #no ticks
        ax.imshow(R[t,:,:],
                  origin='lower',
                  vmin=max(C.clim[0],1), vmax=C.clim[1],
                  cmap='gray')
        ax.text(0.05, 0.075, datetime.fromtimestamp(C.tKeo[t],tz=UTC).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3],
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
def plotRealImg(sim,cam,rawdata,t,makeplot,odir=None):
    """
    sim: histfeas/simclass.py
    cam: histfeas/camclass.py
    t:
    makeplot: list/tuple of requested plots
    odir: output directory (where to write results)

    plots both cameras together,
    and magnetic zenith 1-D cut line
    and 1 degree radar beam red circle centered on magnetic zenith
    """
    ncols = len(cam)
    T=nans(ncols,dtype=datetime)

#    if asi is not None:
#        ncols=3
#        if isinstance(asi,(tuple,list)):
#            pass
#        elif isinstance(asi,(str,Path)):
#            asi = Path(asi).expanduser()
#            if asi.is_dir():
#                asi=list(asi.glob('*.FITS'))

    fg,axs = subplots(nrows=1,ncols=ncols, figsize=(15,12),dpi=dpi,facecolor='black')
    #fg.set_size_inches(15,5) #clips off
    #for i,(R,C,ax) in enumerate(zip(rawdata,cam,axm)):
    for i,C in enumerate(cam):
        if C.usecam: #HiST2 cameras
            T[i] = updateframe(t,rawdata[i],None,cam[i],axs[i],fg) #hold times for all cameras at this time step
        elif C.name=='asi': #ASI
            (opt,_,_,times) = readDASC(C.fn, None,None, treq=T[sim.useCamBool][0])
            C.tKeo = times[:,0]

            updateframe(0,opt['image'],opt['lambda'],C,axs[i],fg)
            overlayrowcol(axs[i],C.hlrows,C.hlcols)
        else:
            raise TypeError('unknown camera {} index {}'.format(C.name,i))

        if i==0:
            axs[0].set_ylabel(datetime.strftime(T[0],'%x')).set_color('limegreen')
            #fg.suptitle(datetime.strftime(T[0],'%x')) #makes giant margins that tight_layout doesn't help, bug
            #fg.text(0.5,0.15,datetime.strftime(T[0],'%x'))#, va='top',ha='center') #bug too
            #fg.tight_layout()
            #fg.subplots_adjust(top=0.95)
   # draw()

    if 'png' in makeplot:
        writeplots(fg,'rawFrame',T[0],makeplot,odir) #FIXME: T[0] is fastest cam now, but needs generalization

    close(fg)

def updateframe(t,raw,wavelen,cam,ax,fg):
    showcb = False

    ttxt='Cam {}:'.format(cam.name)

    if raw.ndim ==3:
        frame = raw[t,...]
    elif raw.ndim==2:
        frame = raw
    elif raw.ndim==1: #GeoData
        frame = raw.reshape((sqrt(raw.size),-1))
    else:
        raise ValueError('ndim==3 or 2')
    #plotting raw uint16 data
    hi = ax.imshow(frame,
                     origin='lower',interpolation='none',
                     #aspect='equal',
                     #extent=(0,C.superx,0,C.supery),
                     vmin=cam.clim[0], vmax=cam.clim[1],
                     cmap='gray',)
                     #norm=LogNorm())
    ax.autoscale(False) # False for case where we put plots on top of image

    if showcb: #showing the colorbar makes the plotting go 5-10x more slowly
        hc = fg.colorbar(hi, ax=ax) #not cax!
        hc.set_label('{} data numbers'.format(raw.dtype))


    dtframe = datetime.fromtimestamp(cam.tKeo[t],tz=UTC)

    if cam.name == 'asi':
        dtstr = datetime.strftime(dtframe,'%H:%M:%S')
        if int(wavelen[t])==428:
            tcolor='blue'
        elif int(wavelen[t])==557:
            tcolor='limegreen'
        elif int(wavelen[t])==630:
            tcolor='red'
        else:
            tcolor='limegreen'
        ttxt += '{} $\lambda$ {:.1f}'.format(dtstr,wavelen[t])
    else:
        dtstr = datetime.strftime(dtframe,'%H:%M:%S.%f')[:-3] #millisecond
        tcolor='limegreen'
        ttxt += '{}'.format(dtstr)



    ax.set_title(ttxt,color=tcolor)

    ax.set_axis_off() #no ticks

    if False:
        ax.set_xlabel('x-pixel')
        if cam.name==0:
            ax.set_ylabel('y-pixel')
#%% plotting 1D cut line
    try:
       ax.plot(cam.cutcol,cam.cutrow,
             marker='.',linestyle='none',color='blue',markersize=1)
        #plot magnetic zenith
       ax.scatter(x=cam.cutcol[cam.angleMagzenind],
               y=cam.cutrow[cam.angleMagzenind],
               marker='o',facecolors='none',color='red',s=500)
    except AttributeError: #asi
       pass
#%% plot cleanup
    ax.grid(False) #in case Seaborn is used
    return dtframe