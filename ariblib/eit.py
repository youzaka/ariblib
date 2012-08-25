#!/usr/bin/env python3.2

from datetime import datetime, timedelta

from ariblib import descriptor

"""Event Information Table nの処理関数群"""

pids = [0x12, 0x26, 0x27]
table_pids = range(0x4E, 0x70)

def tables(ts):
    """Event Information Table を返すジェネレータ"""

    return ts.tables(pids)

def sections(table):
    section_length = ((table[1] & 0x0F) << 8) | table[2]
    index = 14
    sections_last = section_length - 4
    while index < sections_last:
        descriptor_length = ((table[index+10] & 0x0F) << 8) | table[index+11]
        section_last = 12 + descriptor_length
        yield table[index:index+section_last]
        index += section_last

def event_id(section):
    return (section[0] << 8) | section[1]

def start_time(section):
    mjd = (section[2] << 8) | section[3]
    yy_ = int((mjd - 15078.2) / 365.25)
    mm_ = int((mjd - 14956.1 - int(yy_ * 365.25)) / 30.6001)
    k = 1 if 14 <= mm_ <= 15 else 0
    day = mjd - 14956 - int(yy_ * 365.25) - int(mm_ * 30.6001)
    year = 1900 + yy_ + k
    month = mm_ - 1 - k * 12
    hour = ((section[4] & 0xF0) >> 4) * 10 + (section[4] & 0x0F)
    minute = ((section[5] & 0xF0) >> 4) * 10 + (section[5] & 0x0F)
    second = ((section[6] & 0xF0) >> 4) * 10 + (section[6] & 0x0F)
    return datetime(year, month, day, hour, minute, second)

def duration(section):
    hour = ((section[7] & 0xF0) >> 4) * 10 + (section[7] & 0x0F)
    minute = ((section[8] & 0xF0) >> 4) * 10 + (section[8] & 0x0F)
    second = ((section[9] & 0xF0) >> 4) * 10 + (section[9] & 0x0F)
    return timedelta(hours=hour, minutes=minute, seconds=second)

def descriptors(section):
    descriptor_length = ((section[10] & 0x0F) << 8) | section[11]
    descriptors = section[12:12+descriptor_length]
    return descriptor.descriptors(descriptors)


