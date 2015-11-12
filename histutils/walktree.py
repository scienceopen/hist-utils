#!/usr/bin/env python3
"""
Recursively loops for pattern-matching files, like GNU find
Michael Hirsch
Dec 2014
"""
from __future__ import unicode_literals
from six.moves import getcwd
from pathlib2 import Path
from six import string_types

def walktree(root,pat=''):
    """ with pathlib, this functionality is builtin. Left here as compatibility layer
    and to raise awareness of pathlib

    output:
    list with all recursively globbed paths (use sorted() to get a sorted list. Just list() doesn't work.)
    """
    assert isinstance(root,(Path,string_types))

    return sorted(Path(root).expanduser().glob('**/*'+pat))


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='Recursively loops for pattern-matching files, like GNU find')
    p.add_argument('rootdir',help='path including and below which to search',default=getcwd(),nargs='?')
    p.add_argument('pattern',help='text to search for (use double apostrophes and globbing e.g. "myfile*" ',default="*",nargs='?')
    a=p.parse_args()

    found = walktree(a.rootdir,a.pattern)
    print(found)
