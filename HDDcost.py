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

print('quantities are for full data rate')

Zyla = Cam(2560*2160,100,4,1500)
print('\n--------------------------')
print('Zyla')
print('MB/sec: {:.1f}    GB/hour: {:.0f}'.format(Zyla.bytesec/1e6, Zyla.bytehour/1e9))
print('SSD: ${:.2f}/hour'.format(Zyla.HDDcosthour))
print('{} TB SSD fills in {:.2f} hours'.format(Zyla.hddTB,Zyla.hourstorage))

U897 = Cam(512*512,56,8,220)
print('\n--------------------------')
print('Ultra 897')
print('MB/sec: {:.1f}    GB/hour: {:.0f}'.format(U897.bytesec/1e6, U897.bytehour/1e9))
print('HDD: ${:.2f}/hour'.format(U897.HDDcosthour))
print('{} TB HDD fills in {:.1f} hours'.format(U897.hddTB, U897.hourstorage))

U888 = Cam(1024*1024,26,8,220)
print('\n--------------------------')
print('Ultra 888')
print('MB/sec: {:.1f}    GB/hour: {:.0f}'.format(U888.bytesec/1e6, U888.bytehour/1e9))
print('HDD: ${:.2f}/hour'.format(U888.HDDcosthour))
print('{} TB HDD fills in {:.1f} hours'.format(U888.hddTB, U888.hourstorage))

