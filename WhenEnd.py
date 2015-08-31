#!/usr/bin/env python3
"""
calculates what approximate time a .DMCdata file ends, based on inputs:
starttime
fps
xpix,ypix
"""
from __future__ import division
from datetime import timedelta
from dateutil.parser import parse
from argparse import ArgumentParser

p = ArgumentParser(description='calculates what approximate time a .DMCdata file ends, based on inputs')
p.add_argument('starttime',help='date and time of first frame')
p.add_argument('fps',help='frames per second',type=float)
p.add_argument('xypix',help='binned pixel count',nargs=2,type=int)
p.add_argument('filesize',help='file size in bytes of big .DMCdata file',type=int)
p.add_argument('--nheadbytes',help='number of bytes in each frame for header (default 4)',type=int,default=4)
p=p.parse_args()

tstart = parse(p.starttime)
nframes = p.filesize//(p.xypix[0] * p.xypix[1] * 2 + 4)
totalsec = nframes/p.fps

tend = tstart + timedelta(seconds=totalsec)
print('tstart {}  tend {}'.format(tstart,tend))
