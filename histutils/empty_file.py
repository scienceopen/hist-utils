"""
empty_file.py
makes an empty file
in bash you'd do   >myfile or touch myfile
"""
from six import string_types,PY2
from os import makedirs
from pathlib2 import Path
if PY2: FileNotFoundError=IOError

def empty_file(flist):
    if isinstance(flist,(string_types,Path)):
        flist=[flist]

    def _blank(f):
        with f.open('w'):
            pass

    for f in flist:
        f = Path(f)
        try:
            _blank(f)
        except FileNotFoundError:
            makedirs(str(f.parent))
            _blank(f)

if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('dirs',help='directories to create',nargs='+',default='')
    p = p.parse_args()

    empty_file(p.dirs)
