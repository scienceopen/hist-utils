#!/usr/bin/env python
"""
A demo of using Wiener filters efficiently on noisy auroral video
"""
import h5py
from numpy import log10, absolute,diff,hypot,median
from numpy.fft import fft2,fftshift
from scipy.signal import wiener
#
from matplotlib.pyplot import subplots, show,figure
from matplotlib.colors import LogNorm
import seaborn as sns
sns.set_style('whitegrid')
sns.set_context('talk',font_scale=1.4)


fn = 'tests/testframes_cam0.h5' # indistinct aurora

with h5py.File(fn,'r') as f:
    imgs = f['/rawimg'].value.astype(float) #float for fft

im = imgs[0,...]

#%%
u,v = diff(im,axis=1),diff(im,axis=0)
uvmag = hypot(u[1:,:],v[:,1:])

figure(3).clf()
ax = figure(3).gca()
ax.hist(im.ravel(),bins=128)
ax.set_yscale('log')
ax.set_title('hist: image')
ax.set_xlabel('16-bit Data numbers')
ax.set_ylabel('occurrences')
ax.axvline(median(im),linestyle='--',color='red',label='median')
ax.axvline(im.mean(),linestyle='-.',color='black',label='mean')
ax.legend()

figure(2).clf()
fg,axs = subplots(1,2,num=2)

ax = axs[0]
h=ax.imshow(uvmag,# norm=LogNorm(),
            cmap='cubehelix_r',
            vmin=500,vmax=4000,origin='bottom')
fg.colorbar(h,ax=ax)
ax.set_title('|flow|')
ax.set_xlabel('x')
ax.set_ylabel('y')


ax = axs[1]
ax.hist(uvmag.ravel(),bins=128)
ax.set_yscale('log')
#ax.set_xlim((None,5000))
ax.axvline(median(uvmag),linestyle='--',color='red',label='median')
ax.axvline(uvmag.mean(),linestyle='--',color='green',label='mean')
ax.legend()
ax.set_title('hist: |flow|')
ax.set_ylabel('occurrences')
ax.set_xlabel('|flow|')
#%%
figure(1).clf()
fg,ax = subplots(2,2,num=1)

hi=ax[0,0].imshow(im)
ax[0,0].set_title('raw image')
fg.colorbar(hi,ax=ax[0,0])

#%%
Im = fft2(im)

hf=ax[1,0].imshow(20*log10(absolute(fftshift(Im))))
ax[1,0].set_title('F(im)')
fg.colorbar(hf,ax=ax[1,0])
hf.set_clim((90,None))
#%%
fim = wiener(im,7)

hf = ax[0,1].imshow(fim)
ax[0,1].set_title('filtered image')
fg.colorbar(hf,ax=ax[0,1])
#%%
Fim = fft2(fim)
hf=ax[1,1].imshow(20*log10(absolute(fftshift(Fim))))
ax[1,1].set_title('F(fim)')
fg.colorbar(hf,ax=ax[1,1])
hf.set_clim((90,None))

show()