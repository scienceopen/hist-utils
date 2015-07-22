function verifyDASCframeRate(varargin)
%% 
% You can play with framerate, but it looks to me like the frame rate of the
% Poker Flat Research Range DASC all-sky camera is very much varying in a non-monotonic way
%
% I attempt to take the first frame time, and predict time for future frames based
% on a constant per-frame time offset (a.k.a. kinetic rate)
%
p = inputParser;
addOptional(p,'vidfn','~/data/PKR_DASC_20130414_rgb.mpg')
addOptional(p,'startutc',datetime(2013,4,14,6,23,31.8,'timezone','utc'))
addParameter(p,'framerate',1/12.75)
addParameter(p,'framelist',[1,5,15,25,26])
parse(p,varargin{:})
U = p.Results;

kineticrate=1/U.framerate; %picture taken every kineticrate seconds
t0 = U.startutc;
nframe = length(U.framelist);

h = figure(1); clf(h)
set(h,'pos',[50,50,1300,430])
v = VideoReader(U.vidfn);

j=0;
for i = U.framelist
    j=j+1;
    I = read(v,i); 
    subplot(1,nframe,j)
    image(I)
    title(char(t0+seconds(kineticrate*(i-1))))
end


end %function
    