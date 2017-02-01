"""
writes HDF5 huge image files in increments

"""
from pathlib import Path
import h5py
from numpy import string_,uint8,int16

def setupimgh5(fn,Nframetotal,Nrow,Ncol,dtype=int16):
    print('creating {}'.format(fn))
    with h5py.File(str(fn),'w',libver='latest') as f:
        fimg = f.create_dataset('/rawimg',
                 shape =  (Nframetotal,Nrow,Ncol),
                 dtype=dtype,
                 chunks=(1,Nrow,Ncol),
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

def imgwriteincr(fn,imgs,imgslice):
    assert isinstance(fn,Path)

    if isinstance(imgslice,int):
        if imgslice and not (imgslice % 2000):
            print('appending images {} to {}'.format(imgslice,fn))

    assert fn.suffix == '.h5','Expecting to write .h5 file' # avoid accidental overwriting of source file due to misspecified command line

    with h5py.File(str(fn),'r+',libver='latest') as f:
        f['/rawimg'][imgslice,:,:] = imgs
