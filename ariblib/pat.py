#!/usr/bin/env python3.2

"""Program Assocaiton Table nの処理関数群"""

pids = [0x00]

def tables(ts):
    """Program Association Table を返すジェネレータ"""

    return ts.tables(pids)

def sections(table):
    section_length = ((table[1] & 0x0F) << 8) | table[2]
    index = 8
    while index < section_length:
        yield table[index:index+4]
        index += 4

def program_numbers(table):
    for section in sections(table):
        program_number = (section[0] << 8) | section[1]
        pid = ((section[2] & 0x1F) << 8) | section[3]
        yield (program_number, pid)

def pmt_pids(ts):
    for table in tables(ts):
        yield [pid for program_number, pid in program_numbers(table)
               if program_number != 0]

