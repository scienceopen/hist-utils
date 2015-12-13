from __future__ import division,absolute_import,unicode_literals
import logging
from matplotlib.pyplot import figure,draw,subplots
from matplotlib.colors import LogNorm
from numpy import in1d
from datetime import datetime
from pytz import UTC
#
from gridaurora.plots import writeplots

dpi = 100

def plotPlainImg(sim,cam,rawdata,t,makeplot,figh,odir):
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
        if in1d(('png'),makeplot).any():
            writeplots(fg,'cam{}rawFrame'.format(C.name),t,odir)

#%%
def plotRealImg(sim,cam,rawdata,t,makeplot,odir):
    """
    plots both cameras together,
    and magnetic zenith 1-D cut line
    and 1 degree radar beam red circle centered on magnetic zenith
    """
    showcb = False

    fg,axm = subplots(nrows=1,ncols=2, figsize=(15,12),dpi=dpi)
    #fg.set_size_inches(15,5) #clips off
    for R,C,ax in zip(rawdata,cam,axm):
        #FIXME this would need help if one of the cameras isn't plotted (this will probably never happen)
        if R.ndim ==3:
            frame = R[t,...]
        elif R.ndim==2:
            frame = R
        else:
            raise ValueError('ndim==3 or 2')
        #plotting raw uint16 data
        hi = ax.imshow(frame,
                         origin='lower',interpolation='none',
                         #aspect='equal',
                         #extent=(0,C.superx,0,C.supery),
                         vmin=max(C.clim[0],1), vmax=C.clim[1],
                         cmap='gray',)
                         #norm=LogNorm())
        ax.autoscale(False) # False for case where we put plots on top of image

        if showcb: #showing the colorbar makes the plotting go 5-10x more slowly
            hc = fg.colorbar(hi, ax=ax) #not cax!
            hc.set_label(str(R.dtype) + ' data numbers')

        dtframe = datetime.utcfromtimestamp(C.tKeo[t])

        ax.set_title('Cam{}: {}'.format(C.name,dtframe))
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
           logging.debug('skipped plotting cut line on video ind {}'.format(t))
    #%% plot cleanup
        ax.grid(False) #in case Seaborn is used


    draw() #Must have this here or plot doesn't update in animation multiplot mode!

    if in1d(('png'),makeplot).any():
        writeplots(fg,'rawFrame',dtframe,makeplot,odir)
