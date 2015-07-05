#!/usr/bin/env python
import matplotlib
matplotlib.use('Agg') #so Travis doesn't try to plot
from numpy import array,nan
from numpy.testing import assert_allclose, assert_almost_equal
from datetime import datetime
#
try:
    from .airMass import airmass
    from .rawDMCreader import getDMCparam,getDMCframe
    from .plotSolarElev import compsolar
except:
    from airMass import airmass
    from rawDMCreader import getDMCparam,getDMCframe
    from plotSolarElev import compsolar

def test_airmass():
    theta=[-1.,38.]
    Irr,M,I0 = airmass(theta,datetime(2015,7,1,0,0,0))
    assert_allclose(Irr,[nan, 805.13538427])
    assert_allclose(M,[nan,  1.62045712])

def test_rawread():
    bigfn='testframes.DMCdata'
    finf = getDMCparam(bigfn,(512,512),(1,1),None,verbose=2)
    with open(bigfn,'rb') as f:
        testframe,testind = getDMCframe(f,iFrm=1,finf=finf,verbose=2)
    assert testind == 710731
    #test a handful of pixels
    assert (testframe[:5,0] == array([642, 1321,  935,  980, 1114])).all()
    assert (testframe[-5:,-1] == array([2086, 1795, 2272, 1929, 1914])).all()

def test_plotsolar():
    Irr,sunel = compsolar('pfisr',(None,None,None),
                          datetime(2015,7,1,0,0,0), 1, False)
    assert_allclose(Irr[[6,14,6],[2,125,174]], [nan,  216.436431,  405.966392])
    assert_allclose(sunel[[6,14,6],[2,125,174]], [-33.736906, 4.438728, 9.068415])


if __name__ == '__main__':
    test_airmass()
    test_rawread()
    test_plotsolar()