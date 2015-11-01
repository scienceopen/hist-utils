#!/usr/bin/env python
from __future__ import division,absolute_import
from numpy import array,nan,uint16,int64
from numpy.testing import assert_allclose,assert_almost_equal
from datetime import datetime
from pytz import timezone
#
from histutils.airMass import airmass
from histutils.rawDMCreader import goRead
from histutils.compsolar import compsolar
from histutils.diric import diric
from histutils.findnearest import find_nearest
from histutils import fortrandates

def test_findnearest():
    indf,xf = find_nearest([10,15,12,20,14,33],[32,12.01])
    assert_almost_equal(indf,[5,2])
    assert_almost_equal(xf,[33.,12.])

def test_airmass():
    theta=[-1.,38.]
    Irr,M,I0 = airmass(theta,datetime(2015,7,1,0,0,0))
    assert_allclose(Irr,[nan, 805.13538427])
    assert_allclose(M,[nan,  1.62045712])

def test_rawread():
    bigfn='test/testframes.DMCdata'
    framestoplay=(1,2,1)  #this is (start,stop,step) so (1,2,1) means read only the second frame in the file

    testframe, testind,finf,ut1_unix = goRead(bigfn,(512,512),(1,1),framestoplay,verbose=1)

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
    Irr,sunel,Whr = compsolar('pfisr',(None,None,None),
                          datetime(2015,7,1,0,0,0), 1, False)
    assert_allclose(Irr[[16,14,6],[105,155,174]], [ 440.01004384,  419.50384663,  405.96639206])
    assert_allclose(sunel[[6,14,6],[2,125,174]], [-33.736906, 4.438728, 9.068415])

def test_diric():
    assert_allclose(diric(3.,2),0.0707372)
#%% dates
#%% fortrandates
def test_fortrandates():
    adatetime=datetime(2013,7,2,12,0,0)
    yeardec = fortrandates.datetime2yeardec(adatetime)
    assert_allclose(yeardec,2013.5)

    assert fortrandates.yeardec2datetime(yeardec) == adatetime

def test_utc():
    adatetime=datetime(2013,7,2,12,0,0)
    estdt = timezone('EST').localize(adatetime)
    utcdt = fortrandates.forceutc(estdt)
    assert utcdt==estdt
    assert utcdt.tzname()=='UTC'

def test_datetimefortran():
    adatetime=datetime(2013,7,2,12,0,0)
    iyd,utsec,stl= fortrandates.datetime2gtd(adatetime,glon=42)
    assert iyd[0]==183
    assert_allclose(utsec[0],43200)
    assert_allclose(stl[0],14.8)



if __name__ == '__main__':
    test_findnearest()
    test_airmass()
    test_rawread()
    test_plotsolar()
    test_diric()
    test_fortrandates()
    test_utc()
    test_datetimefortran()
