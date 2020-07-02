## selftest of functions
## this is made for GNU Octave only, NOT Matlab !

%!function [testframe, testind] = test_rawread()
%!  bigfn='test/testframes.DMCdata';
%!  framestoplay=2;  %this is (start,stop,step) so (1,2,1) means read only the second frame in the file
%!  [testframe, testind, ~] = rawDMCreader(bigfn,'framereq',framestoplay);
%!endfunction
%!
%!test
%! [testframe, testind] = test_rawread();
%! assert(testind,int64(710731))
%! assert(testframe(1:5,1),uint16([642; 1321;  935;  980; 1114]))
