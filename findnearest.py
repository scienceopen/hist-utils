"""
inputs:
x: array within which to search for x0
x0: singleton or array of values to search for in x

outputs:
idx: index of x nearest to x0
xidx: x[idx]

Note: You should consider using Python's bisect command instead of this function.
I made this function for people coming from Matlab who didn't know about bisect yet.
If you need the index and not just the value, consider the 'sortedcontainers' package
http://grantjenks.com/docs/sortedcontainers/
This find_nearest function does NOT assume sorted input

idea based on http://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array

Michael Hirsch
GPLv3+
"""
from numpy import empty_like,absolute,atleast_1d,asanyarray

def find_nearest(x,x0):
    x = asanyarray(x) #for indexing upon return
    x0 = atleast_1d(x0)
    idx = empty_like(x0,dtype=int)

    for i,xi in enumerate(x0):
       idx[i] = absolute(x-xi).argmin()

    return idx,x[idx]

if __name__ == '__main__': #test case
    print(find_nearest([10,15,12,20,14,33],[32,12.01]))
