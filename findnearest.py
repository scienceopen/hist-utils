from numpy import zeros,abs,argmin,atleast_1d

def find_nearest(x,x0):
    # inputs:
    # x: array within which to search for x0
    # x0: singleton or array of values to search for in x
    # outputs:
    # idx: index of x nearest to x0
    # xidx: x[idx]
    x0 = atleast_1d(x0)
    #idea based on http://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
    idx = zeros(len(x0),dtype=int)

    for i,xi in enumerate(x0):
        idx[i] = abs(x-xi).argmin()

    return idx,x[idx]