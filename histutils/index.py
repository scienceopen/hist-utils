from pathlib import Path
import numpy as np
from typing import Tuple
import logging
from struct import pack, unpack


def getRawInd(fn: Path, BytesPerImage: int, nHeadBytes: int, Nmetadata: int) -> Tuple[int, int]:
    assert isinstance(Nmetadata, int)
    if Nmetadata < 1:  # no header, only raw images
        fileSizeBytes = fn.stat().st_size
        if fileSizeBytes % BytesPerImage:
            logging.error(f'{fn} may not be read correctly, mismatch frame->file size')

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


def req2frame(req, N: int = 0):
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
