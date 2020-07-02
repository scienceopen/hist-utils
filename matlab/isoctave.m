function oct = isoctave()
% Michael Hirsch Oct 2012

oct = exist('OCTAVE_VERSION', 'builtin') == 5;

end
