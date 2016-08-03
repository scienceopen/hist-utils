#!/usr/bin/env python
from . import Path
from numpy import uint16
from datetime import datetime
from pytz import UTC
from matplotlib.pyplot import figure, hist, draw, pause
from matplotlib.colors import LogNorm
#from matplotlib.ticker import ScalarFormatter
#import matplotlib.animation as anim

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
