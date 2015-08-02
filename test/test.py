#!/usr/bin/env python
from numpy import array,nan,uint16,int64
from numpy.testing import assert_allclose
from datetime import datetime
#
from histutils.airMass import airmass
from histutils.rawDMCreader import goRead
from histutils.plotSolarElev import compsolar
from histutils.diric import diric

def test_airmass():
    theta=[-1.,38.]
    Irr,M,I0 = airmass(theta,datetime(2015,7,1,0,0,0))
    assert_allclose(Irr,[nan, 805.13538427])
    assert_allclose(M,[nan,  1.62045712])

def test_rawread():
    bigfn='test/testframes.DMCdata'
    framestoplay=(1,2,1)  #this is (start,stop,step) so (1,2,1) means read only the second frame in the file

    testframe, testind,finf = goRead(bigfn,(512,512),(1,1),framestoplay,verbose=1)

    #these are both tested by goRead
    #finf = getDMCparam(bigfn,(512,512),(1,1),None,verbose=2)
    #with open(bigfn,'rb') as f:
    #    testframe,testind = getDMCframe(f,iFrm=1,finf=finf,verbose=2)
    #test a handful of pixels

    assert testind.dtype == int64
    assert testframe.dtype == uint16
    assert testind == 710731
    assert (testframe[0,:5,0] == array([642, 1321,  935,  980, 1114])).all()
    assert (testframe[0,-5:,-1] == array([2086, 1795, 2272, 1929, 1914])).all()

def test_plotsolar():
    Irr,sunel = compsolar('pfisr',(None,None,None),
                          datetime(2015,7,1,0,0,0), 1, False)
    assert_allclose(Irr[[6,14,6],[2,125,174]], [nan,  216.436431,  405.966392])
    assert_allclose(sunel[[6,14,6],[2,125,174]], [-33.736906, 4.438728, 9.068415])

def test_diric():
    assert_allclose(diric(3.,2),0.0707372)
    
if __name__ == '__main__':
    test_airmass()
    test_rawread()
    test_plotsolar()
    test_diric(0)
