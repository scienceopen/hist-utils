#!/usr/bin/env python3
"""
Plays video contained in HDF5 file, especially from rawDMCreader program.
"""
from __future__ import division,absolute_import
import h5py
#
from histutils.rawDMCreader import doPlayMovie

def playh5movie(h5fn,imgh5):

    with h5py.File(h5fn,'r',libver='latest') as f:
        data = f[imgh5]
        try:
            ut1_unix = f['/ut1_unix']
        except:
            ut1_unix = None
        doPlayMovie(data,1,ut1_unix=ut1_unix)

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='play hdf5 video')
    p.add_argument('h5fn',help='hdf5 .h5 file with video data')
    p.add_argument('imgh5',help='path / variable inside hdf5 file to image stack (default=rawimg)',default='rawimg')
    p = p.parse_args()

    playh5movie(p.h5fn,p.imgh5)
