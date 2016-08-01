from six import integer_types
from numpy import arange,int64

def req2frame(req, N=0):
    """
    output has to be numpy.arange for > comparison
    """
    if isinstance(req,integer_types): #the user is specifying a step size
        return arange(0, N, req, dtype=int64)
    elif len(req) == 1:
        return arange(0, N, req[0], dtype=int64)
    elif len(req) == 2:
        return arange(req[0], req[1], dtype=int64)
    elif len(req) == 3:
        # this is -1 because user is specifying one-based index
        return arange(req[0], req[1], req[2], dtype=int64) - 1 # keep -1 !
    else: # just return all frames
        return arange(N, dtype=int64)
