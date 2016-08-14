from . import Path
from six import integer_types
from numpy import arange,int64
# NOTE: need to use int64 since Numpy thru 1.11 defaults to int32 for dtype=int, and we need int64 for large files

def req2frame(req, N=0):
    """
    output has to be numpy.arange for > comparison
    """
    if req is None:
        frame = arange(N, dtype=int64)
    elif isinstance(req,integer_types): #the user is specifying a step size
        frame = arange(0, N, req, dtype=int64)
    elif len(req) == 1:
        frame = arange(0, N, req[0], dtype=int64)
    elif len(req) == 2:
        frame = arange(req[0], req[1], dtype=int64)
    elif len(req) == 3:
        # this is -1 because user is specifying one-based index
        frame = arange(req[0], req[1], req[2], dtype=int64) - 1 # keep -1 !
    else: # just return all frames
        frame = arange(N, dtype=int64)

    return frame

def dir2fn(ofn,ifn,suffix):
    """
    ofn = filename or output directory, to create filename based on ifn
    ifn = input filename (don't overwrite!)
    suffix = desired file extension e.g. .h5
    """
    if not ofn:
        raise ValueError('must specify something for output, even .')

    ofn = Path(ofn).expanduser()
    ifn = Path(ifn).expanduser()
    assert ifn.is_file()

    if ofn.suffix==suffix: #must already be a filename
        pass
    else: #must be a directory
        assert ofn.is_dir(),'create directory {}'.format(ofn)
        ofn = ofn / ifn.with_suffix(suffix).name

    try:
        assert not ofn.samefile(ifn),' do not overwrite input file! {}'.format(ifn)
    except FileNotFoundError: # a good thing, the output file doesn't exist and hence it's not the input file
        pass

    return ofn
