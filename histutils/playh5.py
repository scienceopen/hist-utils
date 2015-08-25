#/usr/bin/env python3
"""
Plays video contained in HDF5 file, especially from rawDMCreader program.
"""

import h5py
try:
    from .rawDMCreader import doPlayMovie
except:
    from rawDMCreader import doPlayMovie

def playh5movie(h5fn):

    with h5py.File(h5fn,'r',libver='latest') as f:
        data = f['/imgdata']
        doPlayMovie(data,1)

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='play hdf5 video')
    p.add_argument('h5fn',help='hdf5 .h5 file with video data in path /imgdata')
    p = p.parse_args()

    playh5movie(p.h5fn)