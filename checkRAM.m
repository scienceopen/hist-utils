function [OK,newSizeMB,RemainingMB,AvailMemMB] = checkRAM(newSize,newClass)
% Michael Hirsch
% simply checks that your requested memory for the new array won't exceed AVAILABLE RAM 
% based on http://blogs.bu.edu/mhirsch/2013/08/ssh-login-show-load-avg-free-memory-free-disk-etc/
% doesn't work for cells, that's a TODO
% works on Octave/Matlab on Linux, but probably requires Matlab on Windows
% note, I expect this script is optimistic, that Matlab won't always be able to
% create an array using ALL available RAM, but at least you know when you
% certainly CAN'T create an array without digging deep into swap or worse.
% TODO:
% make work on Mac
% test on Cygwin

%% get available RAM

if ismac
warning('this function does not yet work for mac (TODO)')
OK=[]; newSizeMB=[]; RemainingMB =[]; AvailmemMB = [];
return 
end

% it's silly to make three shell calls, should use regexp %FIXME
if isunix 
[~,ret] = unix('cat /proc/meminfo | grep MemFree | tr -s " " | cut -f2 -d" "');
MemFreeMB = str2double(ret) / 1024;
[~,ret] =  unix('cat /proc/meminfo | grep Buffers | tr -s " " | cut -f2 -d" "');
MemBuffMB = str2double(ret) / 1024;
[~,ret] =  unix('cat /proc/meminfo | grep ^Cached | tr -s " " | cut -f2 -d" "');
MemCachMB = str2double(ret) / 1024;

AvailMemMB= uint64(MemFreeMB + MemBuffMB + MemCachMB);

elseif ispc
    [user,sys] = memory; %#ok<NASGU>
    AvailMemMB = uint64(user.MaxPossibleArrayBytes) / 1048576; %sys.PhysicalMemory.Available / 1e6;
end %if
%% variable sizing

switch(newClass)
    case {'single','int32','uint32'}
        bits = 32;
    case {'double','int64','uint64'}
        bits = 64;
    case {'int16','uint16'}
        bits = 16;
    case {'int8','uint8'}
        bits = 8;
    case {'logical','bool'}
        bits = 1;
    case {'string','char'}
        bits = 8; % FIXME is this correct?
    case 'cell'
        error('We didn''t handle cells yet, TODO')
    otherwise, error(['unknown variable class ',newClass])
end

newSizeMB = prod(newSize)*bits/8 / 1e6;

if newSizeMB < AvailMemMB
    OK = true;
    RemainingMB = AvailMemMB - newSizeMB;
else 
    OK = false;
    RemainingMB = [];
end

end
