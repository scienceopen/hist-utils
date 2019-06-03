#!/usr/bin/env python
from pathlib import Path
from numpy import uint16, int64, array
import pytest
from pytest import approx

from histutils.rawDMCreader import goRead
from histutils.hstxmlparse import xmlparam

R = Path(__file__).parent


def test_xmlparse():
    fn = R / 'testframes.xml'
    params = xmlparam(fn)

    assert params['binning'] == 1
    assert params['kineticrate'] == approx(1.88674795e-2)


def test_rawread():
    bigfn = R / 'testframes.DMCdata'
    framestoplay = (1, 2, 1)  # this is (start,stop,step) so (1,2,1) means read only the second frame in the file

    testframe, testind, finf = goRead(bigfn, xyPix=(512, 512), xyBin=(1, 1),
                                      FrameIndReq=framestoplay, verbose=1)

    # these are both tested by goRead
    # finf = getDMCparam(bigfn,(512,512),(1,1),None,verbose=2)
    # with open(bigfn,'rb') as f:
    #    testframe,testind = getDMCframe(f,iFrm=1,finf=finf,verbose=2)
    # test a handful of pixels

    assert testind.dtype == int64
    assert testframe.dtype == uint16
    assert testind == 710730
    assert (testframe[0, :5, 0] == [956,  700, 1031,  730,  732]).all()
    assert (testframe[0, -5:, -1] == [1939, 1981, 1828, 1752, 1966]).all()


def test_nearazel():
    findnearest = pytest.importorskip('histutils.findnearest')

    az = array([[3.,   4,    5],
                [2.5,  3.5,  4.5],
                [2.75, 3.75, 4.75]])
    el = array([[1.1, 1.1, 1.1],
                [1.8, 1.8, 1.8],
                [2.5, 2.5, 2.5]])
    azpts = array([3.6])
    elpts = array([1.5])
    row, col = findnearest.findClosestAzel(az, el, azpts, elpts)

    assert row[0] == 1
    assert col[0] == 1


if __name__ == '__main__':
    pytest.main(['-xrsv', __file__])
