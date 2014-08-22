% [data, rawFrameInd,tUTC] = rawDMCreader(BigFN,xPix,yPix,xBin,yBin,FrameInd,playMovie,Clim,rawFrameRate,startUTC)
% 
% reads uint16 raw data files from DMC
% Tested with Octave 3.6, 3.8 & Matlab R2014a
% Michael Hirsch Dec 2011 / Mar 2012 / Mar 2014
%
% requires: getRawInd.m (custom written script)
%
% INPUTS:
% BigFN: huge .DMCdata filename to read
% xPix: # of x-pixels in sensor {512}
% yPix: # of y-pixels in sensor {512}
% xBin: horizontal binning factor of CCD {1}
% yBin: vertical binning factor of CCD {1}
% FrameInd: Frame numbers to extract from file -- this is NOT raw frame numbers,
% but rather 1-indexed from start of file
% playMovie: if ~= 0, play with pause moviePlay seconds
% clim: for imagesc, sets the upper and lower contrast. E.g. [1000, 1200]
% rawFrameRate: {'auto'} get from XML file (recommended) or manually specify 
% startUTC: {'auto'} get from NMEA file (recommended) or manually specify as  "datenum"
%
% OUTPUTS:
% data: 16-bit data, sorted into frames (view with imagesc)
% rawFrameInd: camera index since acquisition start (used to obtain UTC time of
% frame based on GPS)
% tUTC: estimated UTC time of frame -- unverified
%
% Examples:
% [data,~,tUT] = rawDMCreader('~/HSTdata/DataField/2013-04-14/HST1/2013-04-14T07-00-CamSer7196_frames_363000-1-369200.DMCdata',512,512,1,1,1:100,0.01,[100,4000],'auto','auto');
%
% meteor example  (playing first 100 frames of video):
% [data,~,tUT] = rawDMCreader('/cygdrive/d/2014-03-30/2014-03-30T10-46-CamSer7196.DMCdata',512,512,1,1,1:100,0.01,[100,2000],'auto','auto');
%
% meteor example (extracting first 1000 frames of video, then saving to .mat):
% [data,~,tUT] = rawDMCreader('/cygdrive/d/2014-03-30/2014-03-30T10-46-CamSer7196.DMCdata',512,512,1,1,1:1000,0,[],'auto','auto');
% save('first100.mat','-V7')
% of course one could use fitswrite, h5write, etc. for whatever format one wants.
%
%------------
% flintmax('double') is 2^53 (biggest integer value we can hold in a
% double float variable in Matlab on a 64-bit Operating System)

function [data, rawFrameInd, tUTC] =...
       rawDMCreader(BigFN,xPix,yPix,xBin,yBin,FrameInd,playMovie,Clim,rawFrameRate,startUTC,verbose)

if nargin<1, error('you must specify a file to read'), end
if nargin<2, xPix = 512, yPix = 512, end %#ok<NOPRT> %pixels
if nargin<4, xBin = 1, yBin = 1, end %#ok<NOPRT>
if nargin<6, FrameInd = 'all'; end
if nargin<7, playMovie = 0; end
if nargin<8, Clim = []; end 
if nargin<9, rawFrameRate=[]; end
if nargin<10 || isempty(rawFrameRate), startUTC=[]; end
if nargin<11, verbose = false; end
%%
[rawFrameRate,startUTC] = DMCtimeparams(BigFN,rawFrameRate,startUTC);
%% setup data parameters
% based on settings from .xml file (these stay pretty constant)
SuperX = xPix/xBin;
SuperY = yPix/yBin;
bpp = 16; %bits per pixel
nHeadBytes = 4; %bytes per header frame (32 bits for CCD .DMCdata)
nHeader = nHeadBytes/2; % one 16-bit word = 2 bytes
dFormat = 'uint16=>uint16';  %for Andor CCD
PixelsPerImage= SuperX * SuperY;
BytesPerImage = PixelsPerImage*bpp/8;
BytesPerFrame = BytesPerImage + nHeadBytes;

% get file size
fileInfo= dir(BigFN); 
if isempty(fileInfo), error(['file does not exist: ',BigFN]), end
fileSizeBytes = fileInfo.bytes;

if fileSizeBytes < BytesPerImage
    error(['File size ',int2str(fileSizeBytes),' is smaller than a single image frame!'])
end

nFrame = fileSizeBytes / BytesPerFrame; % by inspection
 %there should be no partial frames

if rem(nFrame,1) ~= 0
    warning(['Looks like I am not reading this file correctly, with BPF ',int2str(BytesPerFrame)])
end

%% get "raw" frame numbers -- that Camera FPGA tags each frame with 
% this raw frame is critical to knowing what time an image was taken, which
% is critical for the usability of this data in light of other sensors
% (radar, optical)
[firstRawInd, lastRawInd] = getRawInd(BigFN,BytesPerImage,nHeadBytes);
if verbose
    display([int2str(nFrame),' frames in file ',BigFN])
    display(['   file size in Bytes: ',sprintf('%ld',fileSizeBytes)])
    display(['first / last raw frame # ',int2str(firstRawInd),' / ',...
             int2str(lastRawInd)])
end
% if no requested frames were specified, read all frames. Otherwise, just
% return the requested frames
if strcmpi(FrameInd,'all')
    FrameInd = 1:nFrame;
end
badReqInd = FrameInd > nFrame;
% check if we requested frames beyond what the BigFN contains
if any(badReqInd)
    error(['You have requested Frames ',int2str(FrameInd(badReqInd)),', which exceed the length of the BigFN'])
end
nFrameExtract = length(FrameInd); %to preallocate properly

nBytesExtract = nFrameExtract*BytesPerFrame;
if verbose
    display(['Extracting ',sprintf('%ld',nBytesExtract),' bytes.'])
end
if nBytesExtract > 2e9
    warning(['This will require ',num2str(nBytesExtract/1e9,'%0.1f'),...
            ' Gigabytes of RAM. Do you have enough RAM?'])
end
%% preallocate
% note: Matlab's default data type is "double float", which takes 64-bits
% per number. That can use up all the RAM of your PC. The data is only
% 16-bit, so to load bigger files, I keep the data 16-bit.
% In analysis programs, we might convert the data frame-by-frame to double
% or single float as we stream the data through an algorithm.  
% That's because many Matlab functions will crash or give unexpected
% results with integers (or single float!)
data = zeros(SuperX,SuperY,nFrameExtract,'uint16'); 
% I created a custom header, but I needed 32-bit numbers. So I stick two
% 16-bit numbers together when writing the data--Matlab needs to unstick
% and restick this number into a 32-bit integer again.
% then I store as double in case we want to do numerical operations --
% uint's can lead to unexpected results!
rawFrameInd = zeros(nFrameExtract,1,'double');
if ~isempty(rawFrameRate)
    tUTC = nan(nFrameExtract,1,'double'); 
else
    tUTC = [];
end
%% read data
fid = fopen(BigFN,'r');
if fid<1, error(['error opening ',BigFN]), end
jFrm = 0;
for iFrame = FrameInd  
    
    jFrm = jFrm + 1; %used for indexing memory
    
    currByte = (iFrame - 1) * BytesPerFrame; %start at beginning of frame
    
    % advance to start of frame in bytes
    fsErr = fseek(fid,currByte,'bof');
    if fsErr
        error(['Could not seek to byte ',currByte,', request ',int2str(jFrm)])
    end
    
    %read data
    %we transpose because Labview writes ROW MAJOR and Matlab is COLUMN MAJOR
    data(:,:,jFrm) = transpose(fread(fid,[SuperX,SuperY],dFormat,0,'l')); %first read the image
    metadata = fread(fid,nHeader,dFormat,0,'l'); % we have to typecast this
    
    %stick two 16-bit numbers together again to make the actual 32-bit raw
    %frame index
    rawFrameInd(jFrm) = double( typecast( [metadata(2), metadata(1)] ,'uint32') );
    if ~isempty(rawFrameRate)
        tUTC(jFrm) = startUTC + ( rawFrameInd(jFrm) - 1 )/rawFrameRate /86400; 
    end
end

fclose(fid);
%% play movie, if user chooses
if playMovie   % ~= 0
  doPlayMovie(data,SuperX,SuperY,nFrameExtract,playMovie,Clim,rawFrameInd,tUTC)
end %for
%% cleanup
if ~nargout, clear, end
end %function

function doPlayMovie(data,nRow,nCol,nFrameExtract,playMovie,Clim,rawFrameInd,tUTC)
%% setup plot
% note: this will plot slowly in Octave 3.6, but Octave 3.8 with FLTK will
% plot this about as fast as Matlab
    h.f = figure(1); clf(1)
    h.ax = axes('parent',h.f);
    switch isempty(Clim)
        case false, h.im = imagesc(zeros(nRow,nCol,'uint16'),Clim);
        case true,  h.im = imagesc(zeros(nRow,nCol,'uint16'));
    end %switch
   %flip the picture back upright.  Different programs have different ideas
   %about what corner of the image is the origin. Or whether to start indexing at (0,0) or (1,1).
    set(h.ax,'ydir','normal') 
    % just some labels
    h.t = title(h.ax,'');
    try
        colormap(h.ax,'gray') %matlab, octave 3.8
    catch
        colormap('gray') %octave 3.6
    end
    h.cb = colorbar('peer',h.ax);
    ylabel(h.cb,'Data Numbers')
    xlabel(h.ax,'x-pixels')
    ylabel(h.ax,'y-pixels')
%% do the plotting    
% setting Cdata like this is much, MUCH faster than repeatedly calling
% imagesc() !
try
    for iFrame = 1:nFrameExtract
     set(h.im,'cdata',single(data(:,:,iFrame))) %convert to single just as displaying
     titlestring = ['Raw Frame # ',int2str(rawFrameInd(iFrame)),...
           '  Relative Frame # ',int2str(iFrame)];
     if ~isempty(tUTC)
         titlestring = [titlestring,'  time: ',datestr(tUTC(iFrame),'yyyy-mm-ddTHH:MM:SS.FFF'),' UTC']; %#ok<AGROW>
     end
     
     set(h.t,'String',titlestring)
     pause(playMovie)
    end
catch ME
    display(iFrame)
    try
    display(tUTC(iFrame))
    display(rawFrameInd(iFrame))
    end
    rethrow(ME)
end
%% cleanup
if nargout==0, clear, end
end %function
