function rawind = utc2rawind(fn,utcdatenum)
% estimates raw frame index of .DMCdata file 
% NOT guaranteed to be correct
% INPUTS
% fn: huge .DMCdata file
% utcdatenum: requested UTC time(s) in datenum() format (24hours=1.0)
% OUTPUTS
% rawind: raw frame indices (one-indexed from start of recording) estimated from
% utc datenum, .xml, and .nmea files


rawFrameRate = 'auto';
startUTC = 'auto';
spd = 86400; %seconds/day

%% estimate frame timing
[rawFrameRate,startUTC] = DMCtimeparams(fn,rawFrameRate,startUTC);
%% esimate raw frame indices
% TODO check for off-by-one error in frame indices
secondsSinceStart = (utcdatenum - startUTC)*spd;
rawind = round(secondsSinceStart * rawFrameRate); %in matlab, better to leave the indices as class double!

end