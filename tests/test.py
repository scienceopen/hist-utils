#!/usr/bin/env python
from pathlib import Path
from numpy import uint16,int64
from numpy.testing import assert_allclose,assert_almost_equal,assert_array_equal,run_module_suite
#
from histutils.rawDMCreader import goRead
from histutils.diric import diric

tdir  = Path(__file__).parent

def test_diric():
    assert_allclose(diric(3.,2),0.0707372)

def test_rawread():
    bigfn = tdir / 'testframes.DMCdata'
    framestoplay=(1,2,1)  #this is (start,stop,step) so (1,2,1) means read only the second frame in the file

    testframe, testind,finf= goRead(bigfn,(512,512),(1,1),framestoplay,verbose=1)

    #these are both tested by goRead
    #finf = getDMCparam(bigfn,(512,512),(1,1),None,verbose=2)
    #with open(bigfn,'rb') as f:
    #    testframe,testind = getDMCframe(f,iFrm=1,finf=finf,verbose=2)
    #test a handful of pixels

    assert testind.dtype == int64
    assert testframe.dtype == uint16
    assert testind == 710730
    assert_array_equal(testframe[0,:5,0],  [ 956,  700, 1031,  730,  732])
    assert_array_equal(testframe[0,-5:,-1],[1939, 1981, 1828, 1752, 1966])



if __name__ == '__main__':
    run_module_suite()
