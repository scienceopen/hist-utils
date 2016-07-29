#!/usr/bin/env python
"""
computes cost of storing camera data
"""
from __future__ import division

class Cam():
    def __init__(self,npix,fps,hddTB,cost,nbit=16):
        self.npix=npix
        self.fps=fps
        self.nbit=nbit
        self.hddTB=hddTB
        self.costTB=cost/self.hddTB

        self.bytesec = self.npix * self.nbit//8 * self.fps
        self.bytehour=self.bytesec*3600

        self.HDDcosthour = self.costTB * self.bytehour/1e12

        self.hourstorage= self.hddTB/(self.bytehour/1e12)

Zyla = Cam(2560*2160,100,2,705)
print('Zyla MByte/sec: {:.1f}'.format(Zyla.bytesec/1e6))
print('Zyla full-frame SSD cost per hour: ${:.2f}'.format(Zyla.HDDcosthour))
print('Zyla {}TB SSD fills in {:.2f} hours'.format(Zyla.hddTB,Zyla.hourstorage))

Ultra = Cam(512*512,56,8,258)
print('Ultra MByte/sec: {:.1f}'.format(Ultra.bytesec/1e6))
print('Ultra full-frame HDD cost per hour: ${:.2f}'.format(Ultra.HDDcosthour))
print('Ultra {}TB HDD fills in {:.1f} hours'.format(Ultra.hddTB,Ultra.hourstorage))