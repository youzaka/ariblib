#/usr/bin/env python3.2

"""字幕処理関係"""

from ariblib.aribgaiji import GAIJI_MAP


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
                try:
                    char2 = self.data.pop(0)
                    yield bytes((char1, char2)).decode('euc-jp')
                except UnicodeDecodeError:
                    gaiji = ((char1 & 0x7f) << 8) | (char2 & 0x7f)
                    if gaiji == 0x7c21:
                        # 次の字幕パケットへセリフが続いていることを示す矢印
                        continue
                    try:
                        yield GAIJI_MAP[gaiji]
                    except KeyError:
                        yield '(0x{:x}{:x}, {}区{}点)'.format(
                            char1, char2, char1 & 0x5f, char2 & 0x5f)
                except IndexError:
                    try:
                        yield GAIJI_MAP[char1]
                    except KeyError:
                        yield '(0x{:x})'.format(char1)
            #elif options.drcs and 0x20 < char1 < 0x2f:
            #    yield str(self.drcs.get(char1, '(0x{:x})'.format(char1)))
            elif char1 in self.mapping:
                yield self.mapping[char1]

    def __str__(self):
        str = ''.join(self).strip()
        self.__str__ = lambda self: str
        return str

class ColoredCProfileString(CProfileString):

    """色付き CProfile 文字列"""

    mapping = {
        0: ' ',
        7: '\a',
        12: '\n',
        13: '\n',
        32: ' ',
        0x80: '\033[30m',
        0x81: '\033[31m',
        0x82: '\033[32m',
        0x83: '\033[33m',
        0x84: '\033[34m',
        0x85: '\033[35m',
        0x86: '\033[36m',
        0x87: '\033[37m',
    }

    def __str__(self):
        str = ''.join(self).strip() + '\033[37m'
        self.__str__ = lambda self: str
        return str

