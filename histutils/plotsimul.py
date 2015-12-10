from __future__ import division,absolute_import
import logging
from matplotlib.pyplot import figure,draw,subplots
from matplotlib.colors import LogNorm
from os.path import join
from numpy import in1d
from datetime import datetime
from pytz import UTC

plotdpi = 100

def plotPlainImg(sim,cam,rawdata,t,makeplot,figh,outdir):
    """http://stackoverflow.com/questions/22408237/named-colors-in-matplotlib"""
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
        if in1d(('rawpng','save'),makeplot).any():
            writeplots(fg,'cam{}rawFrame'.format(C.name),t,outdir)

#%%
def plotRealImg(sim,cam,rawdata,t,makeplot,figh,outdir):
    """
    plots both cameras together, along with magnetic zenith 1-D cut line
    
    """
    showcb = False
    figure(figh).clf()

    fg,axm = subplots(nrows=1,ncols=2,num=figh, dpi=plotdpi)
    #fg.set_size_inches(15,5) #clips off
    for R,C,ax in zip(rawdata,cam,axm):
        #fixme this would need help if one of the cameras isn't plotted (this will probably never happen)

        #plotting raw uint16 data
        hi = ax.imshow(R[t,...],
                         origin='lower',interpolation='none',
                         #aspect='equal',
                         #extent=(0,C.superx,0,C.supery),
                         vmin=max(C.clim[0],1), vmax=C.clim[1],
                         cmap='gray',)
                         #norm=LogNorm())

        if showcb: #showing the colorbar makes the plotting go 5-10x more slowly
            hc = fg.colorbar(hi, ax=ax) #not cax!
            hc.set_label(str(R.dtype) + ' data numbers')
        ax.set_title('Cam{}: {}'.format(C.name, datetime.fromtimestamp(C.tKeo[t],tz=UTC)))
        #ax.set_xlabel('x-pixel')
        if False:#C.name==0:
            ax.set_ylabel('y-pixel')
    #%% plotting 1D cut line
        try:
           ax.plot(C.cutcol,C.cutrow,
                 marker='.',linestyle='none',color='blue',markersize=1)
            #plot magnetic zenith
           ax.scatter(x=C.cutcol[C.angleMagzenind],
                   y=C.cutrow[C.angleMagzenind],
                   marker='o',facecolors='none',color='red',s=500)
        except:
           pass
    #%% plot cleanup
        ax.autoscale(True,tight=True) #fills existing axes
        ax.grid(False) #in case Seaborn is used

    draw() #Must have this here or plot doesn't update in animation multiplot mode!

    if in1d(('rawpng','save'),makeplot).any():
        writeplots(fg,'rawFrame',t,makeplot,outdir)

def writeplots(fg,plotprefix,tInd,method,outdir):
    fmt = 'png'

    draw() #Must have this here or plot doesn't update in animation multiplot mode!

    pfn = join(outdir,(plotprefix + '_t{:03d}.{}'.format(tInd,fmt)))
    logging.info('write {}'.format(pfn))
    fg.savefig(pfn,bbox_inches='tight',dpi=plotdpi,format=fmt)  # this is slow and async
