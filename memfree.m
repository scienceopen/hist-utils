%% find free physical RAM on Windows, Mac, and Linux systems
% currently Matlab doesn't support memory() on Linux/Mac systems
% This function is meant to give free memory on any system that will run Matlab or Octave
%
% This function works on:
% Windows: Matlab, Octave with or without Cygwin
% Mac:     Matlab, Octave
% Linux:   Matlab, Octave
% Android: untested
%
% Output:
% --------
% returns estimate of free physical RAM in bytes
%
% Michael Hirsch 2012

function freebytes = memfree()

if ~isunix  % for Cygwin, isunix=true
    freebytes = memorywindows();
else
    freebytes = memoryunix();
end

disp([num2str(freebytes/1e9,'%0.2f'),' Gbyte available RAM'])

if ~nargout,clear,end
end %function

function freebytes = memoryunix()
[~,msg] = unix('free -mb | grep Mem:');

mems = cell2mat(textscan(msg,'%*s %f %f %f %f %f %f','delimiter',' ','collectoutput',true,'multipleDelimsAsOne',true));
freebytes = mems(1,3)+mems(1,5)+mems(1,6);

end %function

function freebytes = memorywindows()

if isoctave % is windows (and not on Cygwin)
    [~,msg] = system('wmic OS get FreePhysicalMemory /Value');
    freebytes = str2double(msg(26:end))*1e3;
else % is matlab
    [~,s]=memory;
    freebytes = s.PhysicalMemory.Available;
end

end %function
