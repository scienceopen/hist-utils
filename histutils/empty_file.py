"""
empty_file.py
makes an empty file
in bash you'd do   >myfile
"""
from six import string_types
from os import makedirs
from os.path import dirname

def empty_file(flist):
    if isinstance(flist,string_types):
        flist=[flist]
          
    def _blank(f):
        with open(f,'w'): pass
            
    for f in flist:
        try:
            _blank(f)
        except IOError:
            makedirs(dirname(f))
            _blank(f)