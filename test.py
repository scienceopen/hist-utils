#!/usr/bin/env python
from numpy import array,isclose
from numpy.testing import assert_allclose, assert_almost_equal
#%% airmass
from airMass import airmass
theta=38.
Irr,M = airmass(theta)
assert_allclose(Irr,824.93586543623621)
assert_allclose(M,1.6204571165273085)
#%% findnearest
from findnearest import find_nearest
indf,xf = find_nearest([10,15,12,20,14,33],[32,12.01])
assert_almost_equal(indf,[5,2])
assert_almost_equal(xf,[33.,12.])
#%% rawDMCreader
from rawDMCreader import getDMCparam,getDMCframe
import sys
bigfn='testframes.DMCdata'
finf = getDMCparam(bigfn,(512,512),(1,1),None,verbose=2)
with open(bigfn,'rb') as f:
    testframe,testind = getDMCframe(f,iFrm=1,finf=finf,verbose=2)
assert testind == 710731
#test a handful of pixels
assert (testframe[:5,0] == array([642, 1321,  935,  980, 1114])).all()
assert (testframe[-5:,-1] == array([2086, 1795, 2272, 1929, 1914])).all()
#%% plotSolar
from plotSolarElev import compsolar
Irr,sunel = compsolar('pfisr',(None,None,None), '2015', 1, False)
assert isclose(Irr[6,174],   403.17394679495857)
assert isclose(sunel[6,174],  9.0549755440225681)