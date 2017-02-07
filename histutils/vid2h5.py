from pathlib import Path
import logging
from numpy import array,string_,uint8
from datetime import datetime
from pytz import UTC

def vid2h5(data,ut1,rawind,outfn,params,cmdlog=''):
    if not outfn:
        return

    outfn = Path(outfn).expanduser()
    print(f'writing {outfn}')
    #%% saving
    if outfn.suffix == '.h5':
        """
        Reference: https://www.hdfgroup.org/HDF5/doc/ADGuide/ImageSpec.html
        Thanks to Eric Piel of Delmic for pointing out this spec
        * the HDF5 attributess set are necessary to put HDFView into image mode and enables
        other conforming readers to easily play images stacks as video.
        * the string_() calls are necessary to make fixed length strings per HDF5 spec
        """
        import h5py
        #NOTE write mode r+ to not overwrite incremental images
        with h5py.File(str(outfn),'r+',libver='latest') as f:
            if data is not None:
                fimg = f.create_dataset('/rawimg',data=data,
                             compression='gzip',
                             compression_opts=1, #no difference in size from 1 to 5, except much faster to use lower numbers!
                             shuffle=True,
                             fletcher32=True,
                             track_times=True)
                fimg.attrs["CLASS"] = string_("IMAGE")
                fimg.attrs["IMAGE_VERSION"] = string_("1.2")
                fimg.attrs["IMAGE_SUBCLASS"] = string_("IMAGE_GRAYSCALE")
                fimg.attrs["DISPLAY_ORIGIN"] = string_("LL")
                fimg.attrs['IMAGE_WHITE_IS_ZERO'] = uint8(0)

            if ut1 is not None: #needs is not None
                try:
                    print(f'writing from {datetime.utcfromtimestamp(ut1[0]).replace(tzinfo=UTC)} to {datetime.utcfromtimestamp(ut1[-1]).replace(tzinfo=UTC)}')
                    fut1 = f.create_dataset('/ut1_unix',data=ut1,fletcher32=True)
                    fut1.attrs['units'] = 'seconds since Unix epoch Jan 1 1970 midnight'
                except Exception as e:
                    print(e)

            if rawind is not None:
                try:
                    fri = f.create_dataset('/rawind',data=rawind)
                    fri.attrs['units'] = 'one-based index since camera program started this session'
                except Exception as e:
                    logging.error(e)

            try:
                cparam = array((params['kineticsec'],
                            params['rotccw'],
                            params['transpose']==True,
                            params['flipud']==True,
                            params['fliplr']==True,
                            1),
                           dtype=[('kineticsec','f8'),
                                  ('rotccw',    'i1'),
                                  ('transpose', 'i1'),
                                  ('flipud',    'i1'),
                                  ('fliplr',    'i1'),
                                  ('questionable_ut1','i1')]
                           )

                f.create_dataset('/params',data=cparam) #cannot use fletcher32 here, typeerror
            except Exception as e:
                logging.error(e)

            try:
                l = params['sensorloc']
                lparam = array((l[0],l[1],l[2]),     dtype=[('lat','f8'),('lon','f8'),('alt_m','f8')])

                Ld = f.create_dataset('/sensorloc',data=lparam) #cannot use fletcher32 here, typeerror
                Ld.attrs['units'] = 'WGS-84 lat (deg),lon (deg), altitude (meters)'
            except TypeError:
                pass
            except Exception as e:
                logging.error('sensorloc  {}'.format(e))
#%%
            if isinstance(cmdlog,(tuple,list)):
                cmdlog = ' '.join(cmdlog)
            f['/cmdlog'] = str(cmdlog) #cannot use fletcher32 here, typeerror
#%%
            if 'header' in params:
                f['/header'] = str(params['header'])


    elif outfn.suffix == '.fits':
        from astropy.io import fits
        #NOTE the with... syntax does NOT yet work with astropy.io.fits
        hdu = fits.PrimaryHDU(data)
        hdu.writeto(outfn,clobber=False,checksum=True)
        #no close
        """
        Note: the orientation of this FITS in NASA FV program and the preview
        image shown in Python should/must have the same orientation and pixel indexing')
        """

    elif outfn.suffix == '.mat':
        from scipy.io import savemat
        matdata = {'imgdata':data.transpose(1,2,0)} #matlab is fortran order
        savemat(outfn,matdata,oned_as='column')
    else:
        raise ValueError('what kind of file is {}'.format(outfn))
