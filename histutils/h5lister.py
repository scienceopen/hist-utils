#!/usr/bin/env python
"""
recursive list of hdf5 file contents
can also simply in Terminal type:   h5ls -r myFile.h5
this is just an example of traversing the h5 contents, it may not be useful
in and of itself.
Michael Hirsch 2014
"""

import h5py

def h5lister(h5fn):

    with h5py.File(h5fn,'r') as f:

        for dkey,dval in dict(f).iteritems():

            if isinstance(dval,h5py.Dataset):
                print(dval)
            elif isinstance(dval,h5py.Group):
                print(dval)
                for gkey,gval in dict(dval).items():
                    print(gval)

if __name__ == '__main__':
	import sys
	h5lister(sys.argv[1])
