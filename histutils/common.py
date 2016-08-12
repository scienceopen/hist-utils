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
