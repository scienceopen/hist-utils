#!/usr/bin/env python3
"""
Recursively loops for pattern-matching files, like GNU find
this function is case-insensitive (see line 59)
Michael Hirsch
Dec 2014
"""
from os import walk, getcwd #not getcwdu, that's python 2 only
from os.path import join,expanduser,isdir, isfile
from fnmatch import filter
from six import string_types
from warnings import warn
#from stat import S_ISDIR, S_ISREG

def walktree(root,pat):
#%% make list if it's a string
    if isinstance(root,string_types):
        root = [root]
#%%
    found = []
    for r in root:
        r = expanduser(r)
        if isdir(r):
            for top,dirs,files in walk(r):
                for f in filter((ff.lower() for ff in files),pat.lower()):
                    found.append(join(top,f))

            if len(found)==0:
                found=None
        elif isfile(r):
            found.append(r)
        else:
            warn("is {} a file or directory?".format(r))

    return found


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='Recursively loops for pattern-matching files, like GNU find')
    p.add_argument('rootdir',help='path including and below which to search',type=str,default=getcwd(),nargs='?')
    p.add_argument('pattern',help='text to search for (use double apostrophes and globbing e.g. "myfile*" ',type=str,default="*",nargs='?')
    a=p.parse_args()

    found = walktree(a.rootdir,a.pattern)
    print(found)
