#!/usr/bin/env python3
"""
calculates a few times relevant to a .DMCdata file depending on inputs:
starttime
fps
xpix,ypix
and so on
"""
from datetime import timedelta
from dateutil.parser import parse
from argparse import ArgumentParser

p = ArgumentParser(description='calculates what approximate time a .DMCdata file ends, based on inputs')
p.add_argument('starttime',help='date and time of first frame')
p.add_argument('fps',help='frames per second',type=float)
p.add_argument('-k','--frameind',help='frame indices to give times for',nargs='+',type=int)
p.add_argument('--xy',help='binned pixel count',nargs=2,type=int)
p.add_argument('-f','--filesize',help='file size in bytes of big .DMCdata file',type=int)
p.add_argument('--nheadbytes',help='number of bytes in each frame for header (default 4)',type=int,default=4)
p=p.parse_args()

tstart = parse(p.starttime)
#%% find start end times
if p.xy and p.filesize:
    nframes = p.filesize//(p.xy[0] * p.xy[1] * 2 + 4)
    totalsec = nframes/p.fps

    tend = tstart + timedelta(seconds=totalsec)
    print('tstart {}  tend {}'.format(tstart,tend))
#%% find times corresponding to frame #s
if p.frameind:
    for k in p.frameind:
        print('frame {}:  {}'.format(k,tstart + timedelta(seconds=(k-1)*1/p.fps)))
