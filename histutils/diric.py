#!/usr/bin/env python
from __future__ import division
import numpy as np
#try:
#    from numba import jit
#except:
#    print('falling back to Numpy, as Numba is not available.')
"""
Michael Hirsch
based on octave-signal v. 1.10 diric.m
demos use of Oct2Py and Numba (commented Numba for those who just want to use diric)
"""
def diric(x,n):
    n = int(n)
    if n < 1:
        raise RuntimeError('n must be a strictly positive integer')
    return _diric(np.atleast_1d(x),n)

#@jit
def _diric(x,n):
    y = np.sin(n*x/2) / (n*np.sin(x/2))
    #edge case
    badx = np.isnan(y)
    y[badx] = (-1)**((n-1)*x[badx]/(2*np.pi))

    return y


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser('dirichlet function')
    p.add_argument('x',type=float)
    p.add_argument('n',type=int)
    p=p.parse_args()

    print(diric(p.x, p.n))



    if False:
        from numpy.testing import assert_allclose
        x = np.arange(-4*np.pi,4*np.pi,0.1,dtype=float)
        n = 2
        y = diric(x,n)
        try:
            from oct2py import Oct2Py
            oc = Oct2Py(oned_as='column',convert_to_float=True,timeout=5)
            yy = oc.diric(x,n)
            yy = yy.flatten()

            assert_allclose(y,yy)
        except Exception as e:
            print ('skipping comparison')

        try:
            import matplotlib.pyplot as plt
            plt.figure(1); plt.clf()
            plt.plot(x,y,label='python')
            plt.plot(x,yy,'r',label='octave')
            plt.xlabel('x')
            plt.ylabel('diric(x)')
            plt.title('$n={:d}$'.format(n))
            plt.legend()

            plt.show()
        except Exception as e:
            print(f'skipping plotting  {e} ')


