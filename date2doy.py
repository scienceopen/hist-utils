#!/usr/bin/env python
"""
command-line utility to convert date to day of year
"""
from sciencedates import datetime2yd


def date2doy(t):
    yd = str(datetime2yd(t)[0][0])

    year = int(yd[:4])
    doy = int(yd[4:])

    assert 0 < doy < 366

    return doy, year


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('date', help='yyyy-mm-dd')
    P = p.parse_args()

    doy, year = date2doy(P.date)

    print(doy)
