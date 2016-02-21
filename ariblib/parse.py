from datetime import datetime, timedelta
from functools import reduce

from ariblib.aribstr import AribString


def mjd(p):
    """Modified Julian Date[修正ユリウス日]"""

    if p == bytearray(b'\xff\xff\xff\xff\xff'):
        return None
    return datetime(*mjd2datetime(p))


def bcd(p, decimal_point=0):
    """二進化十進数で表現された数値"""

    int_values = map(bcd2int, p)
    value = reduce(lambda x, y: x * 100 + y, int_values)
    return value / (10 ** decimal_point)


def bcdtime(p):
    """二進化十進数で表現された時分秒"""

    if p == bytearray(b'\xff\xff\xff'):
        return None
    hour, minute, second = map(bcd2int, p)
    return timedelta(hours=hour, minutes=minute, seconds=second)


def mjd2datetime(p):
    """mjdを年月日時分秒のタプルとして返す
    ARIB-STD-B10第2部付録Cの通りに実装"""

    mjd = (p[0] << 8) | p[1]
    if len(p) > 2:
        bcd = p[2:]
    else:
        bcd = [0, 0, 0]
    yy_ = int((mjd - 15078.2) / 365.25)
    mm_ = int((mjd - 14956.1 - int(yy_ * 365.25)) / 30.6001)
    k = 1 if 14 <= mm_ <= 15 else 0
    day = mjd - 14956 - int(yy_ * 365.25) - int(mm_ * 30.6001)
    year = 1900 + yy_ + k
    month = mm_ - 1 - k * 12
    return (year, month, day) + tuple(map(bcd2int, bcd))


def bcd2int(bcd):
    """bcdを10進数にする"""

    return ((bcd & 0xF0) >> 4) * 10 + (bcd & 0x0F)


def pts(pts):
    """PTSを求める"""

    pts_hz = 90000
    second = pts / pts_hz
    return timedelta(seconds=second)
