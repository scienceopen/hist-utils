function [rawFrameRate,startUTC] = DMCtimeparams(BigFN,rawFrameRate,startUTC)

[BigDir,BigStem] = fileparts(BigFN);
% handle the case where we have a partial filename (with _frames....)
BigStem = regexp(BigStem,'.*CamSer\d{3,6}(?<=.*)','match'); 
if ~isempty(BigStem) %old files might not have this naming scheme
    BigStem=BigStem{1};
else
    %TODO make work using raw frame indices like Python
    rawFrameRate = [];
    startUTC = [];
    return
end
%% use XML file or user specification to determine frame rate
if ~isempty(rawFrameRate)
   if strcmpi(rawFrameRate,'auto') % grep XML
     XMLfn = [BigDir,'/',BigStem,'.xml'];
     %crude but works
     xmltxt=[]; 
     lbtxt = '<I32><Name>Number Of iXon Pulses</Name><Val>';  latxt = '</Val></I32>';
     regtxt = ['(?<=',lbtxt,')','\d{1,4}','(?=',latxt,')'];
     display(['finding framerate, using regexp ',regtxt])
     fidxml = fopen(XMLfn,'r');
     while ~feof(fidxml)
      xmltxt = [xmltxt, fgetl(fidxml)]; %#ok<AGROW> %easier to parse w/o newlines
     end %while
     frMatch = regexp(xmltxt,regtxt,'match');
     if ~isempty(frMatch),  rawFrameRate = str2double(frMatch); end
   elseif isnumeric(rawFrameRate)%use user specified frame rate
     rawFrameRate = double(rawFrameRate);
   else
       error(['unknown frame rate ',rawFrameRate])
   end %if strcmpi auto
   display(['using frame rate ',num2str(rawFrameRate),' Hz'])
   fclose(fidxml);
else
   %do nothing
end %if isemptyFrameRate
%% use nmea file or user specification to determine start time 
if ~isempty(startUTC)
   if strcmpi(startUTC,'auto') % grep XML
     NMEAfn = [BigDir,'/',BigStem,'.nmea'];
     %crude but works
     lbtxt = '\$GPRMC,';  latxt = ',[AV],';
     regtxt = ['(?<=',lbtxt,')','\d{6}','(?=',latxt,')'];
     display(['finding startUTC, using regexp ',regtxt])
     fidnmea = fopen(NMEAfn,'r');
     while ~feof(fidxml)
      nmeatxt = fgetl(fidnmea); % %easier to parse w/o newlines
      if strcmp(nmeatxt(1:6),'$GPRMC')
          %keeps only the last GPRMC sentence
          gprmc = textscan(nmeatxt,'%s %d %s %f %s %f %s %f %f %d %f %s','delimiter',',','emptyvalue',nan);
      end
     end %while
      dates = int2str(gprmc{10}); %for ensuring no decimal point is thrown in
      times = int2str(gprmc{2}); %likewise

      if ~isempty(dates) && all(~isnan(dates)), 
          
          startUTC = datenum([dates,times],'ddmmyyHHMMSS'); 
      end %don't want nan's
   elseif isnumeric(startUTC) && length(startUTC)==6 %use user specified frame rate
     startUTC = datenum(startUTC);
   elseif isnumeric(startUTC) && length(startUTC) == 1 
       % assume already datenum
   else
       error(['unknown starttime ',startUTC])
   end %if strcmpi auto
   display(['using start time ',datestr(startUTC),' UTC']) 
   fclose(fidnmea);
end %is empty startUTC

end %function
