#!/usr/bin/env python
import matplotlib
matplotlib.use('Agg') #so Travis doesn't try to plot
from numpy import array,isclose,nan
from numpy.testing import assert_allclose, assert_almost_equal
from datetime import datetime
#%% airmass
from airMass import airmass
theta=[-1.,38.]
Irr,M,I0 = airmass(theta,datetime(2015,7,1,0,0,0))
assert_allclose(Irr,[nan, 805.13538427])
assert_allclose(M,[nan,  1.62045712])
#%% findnearest
from findnearest import find_nearest
indf,xf = find_nearest([10,15,12,20,14,33],[32,12.01])
assert_almost_equal(indf,[5,2])
assert_almost_equal(xf,[33.,12.])
#%% rawDMCreader
from rawDMCreader import getDMCparam,getDMCframe
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
Irr,sunel = compsolar('pfisr',(None,None,None),
                      datetime(2015,7,1,0,0,0), 1, False)
assert_allclose(Irr[[6,14,6],[2,125,174]], [nan,  216.59600031,  405.51953114],rtol=1e-1)
assert_allclose(sunel[[6,14,6],[2,125,174]], [-33.70002094,4.44227179,9.0549755440225681],rtol=1e-2)
