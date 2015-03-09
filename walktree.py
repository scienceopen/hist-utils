#!/usr/bin/env python3
"""
Recursively loops for pattern-matching files, like GNU find
Michael Hirsch
Dec 2014
"""
from os import walk, getcwd #not getcwdu, that's python 2 only
from os.path import join,expanduser,isdir, isfile
from fnmatch import filter
#from stat import S_ISDIR, S_ISREG

def walktree(root,pat):
    root = expanduser(root)
    if isdir(root):
        found = []

        for top,dirs,files in walk(root):
            for f in filter(files,pat):
                found.append(join(top,f))

        if len(found)==0:
            found=None
    elif isfile(root):
        found = [root]
    else:
        exit("is " + root + " a file or directory?")

    return found


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='Recursively loops for pattern-matching files, like GNU find')
    p.add_argument('rootdir',help='path including and below which to search',type=str,default=getcwd(),nargs='?')
    p.add_argument('pattern',help='text to search for (use double apostrophes and globbing e.g. "myfile*" ',type=str)
    a=p.parse_args()
    found = walktree(a.rootdir,a.pattern)
    print(found)
