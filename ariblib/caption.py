from datetime import timedelta
import itertools

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
    strings = {}

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
                        yield ''
                except IndexError:
                    try:
                        yield GAIJI_MAP[char1]
                    except KeyError:
                        yield ''
            elif 0x20 < char1 < 0x2f:
                if char1 in self.drcs:
                    if self.drcs[char1] in mapping:
                        yield mapping[self.drcs[char1]]
                    else:
                        yield ''
            elif char1 in self.mapping:
                yield self.mapping[char1]

    def __str__(self):
        str = ''.join(self).strip()
        self.__str__ = lambda self: str
        return str


def absolutize(captions, base, delta=0):
    """相対時間で記述されている字幕情報を絶対時間に変換する"""

    delta = timedelta(seconds=delta)
    for caption in captions:
        if 'delta' not in caption:
            continue
        pts = caption['delta']
        if pts > base:
            relative_delta = pts - base - delta
        else:
            pts_max = timedelta(seconds=8589934591 / 90000)
            relative_delta = pts + pts_max - base - delta

        caption['timestamp'] = relative_delta
        yield caption


def srt_timestamp(timedelta):
    seconds = int(timedelta.total_seconds())
    return '{:02d}:{:02d}:{:02d},{:03d}'.format(
        seconds // 3600, (seconds % 3600) // 60, seconds % 60,
        timedelta.microseconds // 1000)


def srts(captions):
    number = 0
    prev = None
    for caption in captions:
        if prev:
            yield "{}\n{} --> {}\n{}\n\n".format(
                number, srt_timestamp(prev['timestamp']),
                srt_timestamp(caption['timestamp']), prev['body'])
        number += 1
        prev = caption
