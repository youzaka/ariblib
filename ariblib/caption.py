#/usr/bin/env python3.2

from ariblib.aribgaiji import GAIJI_MAP

"""字幕 PES の処理関数群"""

def tables(ts):
    caption_pid = ts.get_caption_pid()
    return ts.tables([caption_pid])

def sections(table):
    PES_header_data_length = table[8]
    PES_data_packet_header_length = table[11+PES_header_data_length] & 0x0F
    index = 12 + PES_header_data_length + PES_data_packet_header_length
    data_group_id = (table[index] & 0xFC) >> 2
    if data_group_id in (0x00, 0x20):
        num_languages = table[index+6]
        index += 7 + num_languages * 5
    else:
        index += 6
    data_unit_loop_length = ((table[index] << 16) |
                              table[index+1] << 8) | table[index+2]
    loop_index = 0
    while loop_index < data_unit_loop_length:
        data_unit_size = ((table[index+5+loop_index] << 16
                          ) | table[index+6+loop_index] << 8
                         ) | table[index+7+loop_index]
        start = index + 4 + loop_index
        end = start + 4 + data_unit_size
        yield table[start:end]
        loop_index += data_unit_size + 5

def data_unit_parameter(section):
    return section[0]
def data_unit_data(section):
    return section[4:]

class CProfileString(object):
    """CProfile文字列"""
    mapping = {
        0: ' ',
        7: '\a',
        12: '\n',
        13: '\n',
        32: ' ',
    }

    drcs = {}

    def __init__(self, data):
        self.data = data

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.character())

    def character(self):
        """一文字ずつUnicode型として返すジェネレータ"""
        while self.data:
            char1 = self.data.pop(0)
            if 0xa0 < char1 < 0xff:
                char2 = self.data.pop(0)
                try:
                    yield bytes((char1, char2)).decode('euc-jp')
                except UnicodeDecodeError:
                    gaiji = ((char1 & 0x7f) << 8) | (char2 & 0x7f)
                    if gaiji == 0x7c21:
                        # 次の字幕パケットへセリフが続いていることを示す矢印
                        continue
                    try:
                        yield GAIJI_MAP[gaiji]
                    except KeyError:
                        yield '(0x{:x}{:x})'.format(char1, char2)
            #elif options.drcs and 0x20 < char1 < 0x2f:
            #    yield str(self.drcs.get(char1, '(0x{:x})'.format(char1)))
            elif char1 in self.mapping:
                yield self.mapping[char1]

    def __str__(self):
        return ''.join(self).strip()

