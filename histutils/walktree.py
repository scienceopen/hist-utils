#!/usr/bin/env python3
"""
Recursively loops for pattern-matching files, like GNU find
Michael Hirsch
Dec 2014
"""
from six.moves import getcwd
from pathlib2 import Path
#from os import walk
#from os.path import join,expanduser,isdir, isfile
#from fnmatch import filter
#from six import string_types
#from warnings import warn
#from stat import S_ISDIR, S_ISREG

def walktree(root,pat=''):
    """ with pathlib, this functionality is builtin. Left here as compatibility layer
    and to raise awareness of pathlib

    output:
    generator with all recursively globbed paths (use sorted() to get a sorted list. Just list() doesn't work.)
    """
    return Path(root).expanduser().glob('**/*'+pat)


#def walktree_obsolete(root,pat):
##%% make list if it's a string
#    if isinstance(root,string_types):
#        root = [root]
##%%
#    found = []
#    for r in root:
#        r = expanduser(r)
#        if isdir(r):
#            for top,dirs,files in walk(r):
#                # using .lower makes output lower too. Maybe need to explicitly iterate
#                #for f in filter((ff.lower() for ff in files),pat.lower()):
#                for f in filter(files,pat):
#                    found.append(join(top,f))
#        elif isfile(r):
#            found.append(r)
#        else:
#            warn("is {} a file or directory?".format(r))
#
#    return found


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='Recursively loops for pattern-matching files, like GNU find')
    p.add_argument('rootdir',help='path including and below which to search',default=getcwd(),nargs='?')
    p.add_argument('pattern',help='text to search for (use double apostrophes and globbing e.g. "myfile*" ',default="*",nargs='?')
    a=p.parse_args()

    found = walktree(a.rootdir,a.pattern)
    print(found)
