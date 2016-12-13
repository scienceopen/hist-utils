#!/usr/bin/env python
"""
A demo of using Wiener filters efficiently on noisy auroral video
"""
import h5py
from numpy import log10, absolute
from numpy.fft import fft2,fftshift
from scipy.signal import wiener
#
from matplotlib.pyplot import subplots, show,figure


fn = 'tests/testframes_cam0.h5'

with h5py.File(fn,'r') as f:
    imgs = f['/rawimg'].value.astype(float) #float for fft

im = imgs[0,...]


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