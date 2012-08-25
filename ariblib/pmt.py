#!/usr/bin/env python3.2

"""Program Map Table の処理関数群"""

from ariblib import descriptor

pids = []
table_ids = [0x02]

def tables(ts):
    """Program Map Table を返すジェネレータ"""

    return ts.tables(pids)

def sections(table):
    section_length = ((table[1] & 0x0F) << 8) | table[2]
    program_info_length = ((table[10] & 0x0F) << 8) | table[11]
    index = 12 + program_info_length
    sections_last = section_length - 4
    while index < sections_last:
        ES_info_length = ((table[index+3] & 0x0F) << 8) | table[index+4]
        section_last = ES_info_length + 5
        yield table[index:index+section_last]
        index += section_last

def stream_type(section):
    return section[0]

def elementary_pid(section):
    return ((section[1] & 0x1F) << 8) | section[2]

def descriptors(section):
    ES_info_length = ((section[3] & 0x0F) << 8) | section[4]
    descriptors = section[5:5+ES_info_length]
    return descriptor.descriptors(descriptors)

