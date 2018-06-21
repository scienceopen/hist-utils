from pathlib import Path
from datetime import datetime
from pytz import UTC
import shutil
import h5py
import numpy as np
import logging
from struct import pack, unpack
from typing import Tuple, Union
# NOTE: need to use int64 since Numpy thru 1.11 defaults to int32 on Windows for dtype=int, and we need int64 for large files


def write_quota(outbytes: int, outfn: Path) -> Union[None, int]:
    """
    aborts writing if not enough space on drive to write
    """
    if not outfn:
        return None

    anch = Path(outfn).resolve().anchor
    freeout = shutil.disk_usage(anch).free

    if freeout < 10 * outbytes:
        raise IOError(f'out of disk space on {anch}.'
                      '{freeout/1e9} GB free, wanting to write {outbytes/1e9} GB.')

    return freeout


def sixteen2eight(I: np.ndarray, Clim: tuple) -> np.ndarray:
    """
    scipy.misc.bytescale had bugs

    inputs:
    ------
    I: 2-D Numpy array of grayscale image data
    Clim: length 2 of tuple or numpy 1-D array specifying lowest and highest expected values in grayscale image
    Michael Hirsch, Ph.D.
    """
    Q = normframe(I, Clim)
    Q *= 255  # stretch to [0,255] as a float
    return Q.round().astype(np.uint8)  # convert to uint8


def normframe(I: np.ndarray, Clim: tuple) -> np.ndarray:
    """
    inputs:
    -------
    I: 2-D Numpy array of grayscale image data
    Clim: length 2 of tuple or numpy 1-D array specifying lowest and highest expected values in grayscale image
    """
    Vmin = Clim[0]
    Vmax = Clim[1]

    # stretch to [0,1]
    return (I.astype(np.float32).clip(Vmin, Vmax) - Vmin) / (Vmax - Vmin)


def getRawInd(fn: Path, BytesPerImage: int, nHeadBytes: int, Nmetadata: int) -> Tuple[int, int]:
    assert isinstance(Nmetadata, int)
    if Nmetadata < 1:  # no header, only raw images
        fileSizeBytes = fn.stat().st_size
        if fileSizeBytes % BytesPerImage:
            logging.error(
                f'{fn} may not be read correctly, mismatch frame->file size')

        firstRawIndex = 1  # definition, one-based indexing
        lastRawIndex = fileSizeBytes // BytesPerImage
    else:  # normal case 2013-2016
        # gets first and last raw indices from a big .DMCdata file
        with fn.open('rb') as f:
            f.seek(BytesPerImage, 0)  # get first raw frame index
            firstRawIndex = meta2rawInd(f, Nmetadata)

            f.seek(-nHeadBytes, 2)  # get last raw frame index
            lastRawIndex = meta2rawInd(f, Nmetadata)

    return firstRawIndex, lastRawIndex


def meta2rawInd(f, Nmetadata):
    assert isinstance(Nmetadata, int)

    if Nmetadata < 1:
        rawind = None  # undefined
    else:
        # FIXME works for .DMCdata version 1 only
        metad = np.fromfile(f, dtype=np.uint16, count=Nmetadata)
        metad = pack('<2H', metad[1], metad[0])  # reorder 2 uint16
        rawind = unpack('<I', metad)[0]  # always a tuple

    return rawind


def req2frame(req, N: int=0):
    """
    output has to be numpy.arange for > comparison
    """
    if req is None:
        frame = np.arange(N, dtype=np.int64)
    elif isinstance(req, int):  # the user is specifying a step size
        frame = np.arange(0, N, req, dtype=np.int64)
    elif len(req) == 1:
        frame = np.arange(0, N, req[0], dtype=np.int64)
    elif len(req) == 2:
        frame = np.arange(req[0], req[1], dtype=np.int64)
    elif len(req) == 3:
        # this is -1 because user is specifying one-based index
        frame = np.arange(req[0], req[1], req[2],
                          dtype=np.int64) - 1  # keep -1 !
    else:  # just return all frames
        frame = np.arange(N, dtype=np.int64)

    return frame


def dir2fn(ofn, ifn, suffix) -> Union[None, Path]:
    """
    ofn = filename or output directory, to create filename based on ifn
    ifn = input filename (don't overwrite!)
    suffix = desired file extension e.g. .h5
    """
    if not ofn:  # no output file desired
        return None

    ofn = Path(ofn).expanduser()
    ifn = Path(ifn).expanduser()
    assert ifn.is_file()

    if ofn.suffix == suffix:  # must already be a filename
        pass
    else:  # must be a directory
        assert ofn.is_dir(), f'create directory {ofn}'
        ofn = ofn / ifn.with_suffix(suffix).name

    try:
        assert not ofn.samefile(ifn), f'do not overwrite input file! {ifn}'
    except FileNotFoundError:  # a good thing, the output file doesn't exist and hence it's not the input file
        pass

    return ofn


def splitconf(conf, key, i=None, dtype=float, fallback=None, sep=','):
    if conf is None:
        return fallback

    if isinstance(conf, dict):
        try:
            return conf[key][i]
        except TypeError:
            return conf[key]
        except KeyError:
            return fallback

    if i is not None:
        assert isinstance(i, (int, slice)), 'single integer index only'

    if isinstance(key, (tuple, list)):
        if len(key) > 1:  # drilldown
            return splitconf(conf[key[0]], key[1:], i, dtype, fallback, sep)
        else:
            return splitconf(conf, key[0], i, dtype, fallback, sep)
    elif isinstance(key, str):
        val = conf.get(key, fallback=fallback)
    else:
        raise TypeError(f'invalid key type {type(key)}')

    try:
        return dtype(val.split(sep)[i])
    except (ValueError, AttributeError, IndexError):
        return fallback
    except TypeError:
        if i is None:
            try:
                # return list of all values instead of just one
                return [dtype(v) for v in val.split(sep)]
            except ValueError:
                return fallback
        else:
            return fallback
# %% HDF5


def setupimgh5(f: Union[Path, h5py.File],
               Nframetotal: int, Nrow: int, Ncol: int, dtype=np.uint16,
               writemode='r+', key='/rawimg', cmdlog: str=None):
    """
    f: HDF5 handle (or filename)

    h: HDF5 dataset handle
    """
    if isinstance(f, (str, Path)):  # assume new HDF5 file wanted
        f = Path(f).expanduser()
        if f.is_dir():
            raise IOError(
                'must provide specific HDF5 filename, not just a directory')

        print('creating', f)
        with h5py.File(f, writemode) as F:
            setupimgh5(F, Nframetotal, Nrow, Ncol, dtype, writemode, key)

    elif isinstance(f, h5py.File):
        h = f.create_dataset(key,
                             shape=(Nframetotal, Nrow, Ncol),
                             dtype=dtype,
                             chunks=(1, Nrow, Ncol),  # each image is a chunk
                             compression='gzip',
                             # no difference in filesize from 1 to 5, except much faster to use lower numbers!
                             compression_opts=1,
                             shuffle=True,
                             fletcher32=True,
                             track_times=True)
        h.attrs["CLASS"] = np.string_("IMAGE")
        h.attrs["IMAGE_VERSION"] = np.string_("1.2")
        h.attrs["IMAGE_SUBCLASS"] = np.string_("IMAGE_GRAYSCALE")
        h.attrs["DISPLAY_ORIGIN"] = np.string_("LL")
        h.attrs['IMAGE_WHITE_IS_ZERO'] = np.uint8(0)

        if cmdlog and isinstance(cmdlog, str):
            f['/cmdlog'] = cmdlog
    else:
        raise TypeError(
            f'{type(f)} is not correct, must be filename or h5py.File HDF5 file handle')


def vid2h5(data: np.ndarray, ut1, rawind, ticks, outfn: Path, P: dict, i: int=0,
           Nfile: int=1, det=None, tstart=None, cmdlog: str=None):
    assert outfn, 'must provide a filename to write'

    outfn = Path(outfn).expanduser()
    assert not outfn.is_dir(
    ), 'must provide FILEname, you provided directory {outfn}'
    outfn.parent.mkdir(exist_ok=True)

    txtupd = f'convert file {i} / {Nfile}'
    if 'spoolfn' in P:
        txtupd += f' {P["spoolfn"].name}'
    txtupd += f' => {outfn}'
    """
    note if line wraps (>80 characters), this in-place update breaks.
    """
    print(txtupd + '\r', end="")
    # %% saving
    if outfn.suffix == '.h5':
        """
        Reference: https://www.hdfgroup.org/HDF5/doc/ADGuide/ImageSpec.html
        Thanks to Eric Piel of Delmic for pointing out this spec
        * the HDF5 attributess set are necessary to put HDFView into image mode and enables
        other conforming readers to easily play images stacks as video.
        * the string_() calls are necessary to make fixed length strings per HDF5 spec
        """
        # NOTE write mode r+ to not overwrite incremental images
        if outfn.is_file():
            writemode = 'r+'  # append
        else:
            writemode = 'w'

        if data is not None:

            N = data.shape[0] * Nfile
            ind = slice(i * data.shape[0], (i + 1) * data.shape[0])
        else:  # FIXME haven't reevaluated for update only case
            for q in (ut1, rawind, ticks):
                if q is not None:
                    N = len(q)
                    break
            ind = slice(None)

        with h5py.File(outfn, writemode) as f:
            if data is not None:
                if 'rawimg' not in f:  # first run
                    setupimgh5(f, N, data.shape[1], data.shape[2])

                f['/rawimg'][ind, ...] = data

            if ut1 is not None:
                print(
                    f'writing from {datetime.utcfromtimestamp(ut1[0]).replace(tzinfo=UTC)} to {datetime.utcfromtimestamp(ut1[-1]).replace(tzinfo=UTC)}')
                if 'ut1_unix' not in f:
                    fut1 = f.create_dataset(
                        '/ut1_unix', shape=(N,), dtype=float, fletcher32=True)
                    fut1.attrs['units'] = 'seconds since Unix epoch Jan 1 1970 midnight'

                f['/ut1_unix'][ind] = ut1

            if tstart is not None and 'tstart' not in f:
                f['/tstart'] = tstart

            if rawind is not None:
                if 'rawind' not in f:
                    fri = f.create_dataset(
                        '/rawind', shape=(N,), dtype=np.int64, fletcher32=True)
                    fri.attrs['units'] = 'one-based index since camera program started this session'

                f['/rawind'][ind] = rawind

            if ticks is not None:
                if 'ticks' not in f:
                    ftk = f.create_dataset(
                        '/ticks', shape=(N,), dtype=np.uint64, fletcher32=True)  # Uint64
                    ftk.attrs['units'] = 'FPGA tick counter for each image frame'

                f['/ticks'][ind] = ticks

            if 'spoolfn' in P:
                # http://docs.h5py.org/en/latest/strings.html
                if 'spoolfn' not in f:
                    fsp = f.create_dataset(
                        '/spoolfn', shape=(N,), dtype=h5py.special_dtype(vlen=bytes))
                    fsp.attrs['description'] = 'input filename data was extracted from'

                f['/spoolfn'][ind] = P['spoolfn'].name

            if det is not None:
                if 'detect' not in f:
                    fdt = f.create_dataset('/detect', shape=(N,), dtype=int)
                    fdt.attrs['description'] = '# of auroral detections this frame'

                f['/detect'][i] = det[i]

            if 'params' not in f:
                cparam = np.array((
                    P['kineticsec'],
                    P['rotccw'],
                    P['transpose'],
                    P['flipud'],
                    P['fliplr'],
                    1),
                    dtype=[('kineticsec', 'f8'),
                           ('rotccw', 'i1'),
                           ('transpose', 'i1'),
                           ('flipud', 'i1'),
                           ('fliplr', 'i1'),
                           ('questionable_ut1', 'i1')]
                )

                # cannot use fletcher32 here, typeerror
                f.create_dataset('/params', data=cparam)

            if 'sensorloc' not in f and 'sensorloc' in P:
                loc = P['sensorloc']
                lparam = np.array((loc[0], loc[1], loc[2]),
                                  dtype=[('lat', 'f8'), ('lon', 'f8'), ('alt_m', 'f8')])

                # cannot use fletcher32 here, typeerror
                Ld = f.create_dataset('/sensorloc', data=lparam)
                Ld.attrs['units'] = 'WGS-84 lat (deg),lon (deg), altitude (meters)'

            if 'cmdlog' not in f:
                if isinstance(cmdlog, (tuple, list)):
                    cmdlog = ' '.join(cmdlog)
                # cannot use fletcher32 here, typeerror
                f['/cmdlog'] = str(cmdlog)

            if 'header' not in f and 'header' in P:
                f['/header'] = str(P['header'])

            if 'hdf5version' not in f:
                f['/hdf5version'] = h5py.version.hdf5_version_tuple

    elif outfn.suffix == '.fits':
        from astropy.io import fits
        # NOTE the with... syntax does NOT yet work with astropy.io.fits
        hdu = fits.PrimaryHDU(data)
        hdu.writeto(outfn, clobber=False, checksum=True)
        # no close
        """
        Note: the orientation of this FITS in NASA FV program and the preview
        image shown in Python should/must have the same orientation and pixel indexing')
        """

    elif outfn.suffix == '.mat':
        from scipy.io import savemat
        # matlab is fortran order
        matdata = {'imgdata': data.transpose(1, 2, 0)}
        savemat(outfn, matdata, oned_as='column')
    else:
        raise ValueError(f'what kind of file is {outfn}')


def imgwriteincr(fn: Path, imgs, imgslice):
    """
    writes HDF5 huge image files in increments
    """
    if isinstance(imgslice, int):
        if imgslice and not (imgslice % 2000):
            print(f'appending images {imgslice} to {fn}')

    if isinstance(fn, Path):
        # avoid accidental overwriting of source file due to misspecified command line
        assert fn.suffix == '.h5', 'Expecting to write .h5 file'

        with h5py.File(fn, 'r+') as f:
            f['/rawimg'][imgslice, :, :] = imgs
    elif isinstance(fn, h5py.File):
        f['/rawimg'][imgslice, :, :] = imgs
    else:
        raise TypeError(
            f'{fn} must be Path or h5py.File instead of {type(fn)}')
