from numpy import zeros,abs,argmin

def find_nearest(x,x0):
    #idead based on http://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
    idx = zeros(len(x0),dtype=int)

    for i,xi in enumerate(x0):
        idx[i] = abs(x-xi).argmin()

    return idx,x[idx]