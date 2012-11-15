#!/usr/bin/env python3.2

"""ビット列表記の実装
仕様書ではビット列表記は全て小文字になっているので、ここで実装するクラスも全て小文字とする
"""

from datetime import datetime, timedelta
from functools import reduce

from ariblib.aribstr import AribString

try:
    callable
except NameError:
    from types import FunctionType
    def callable(function):
        return function.__class__ is FunctionType

def meta_cache(suffix):
    """real_length, real_count用のキャッシュデコレータ"""

    def cache(func):
        def cached(self, instance):
            cache_name = '_{}_{}'.format(self.name, suffix)
            caches = instance.__dict__
            if cache_name in caches:
                return caches[cache_name]
            result = func(self, instance)
            caches[cache_name] = result
            return result
        return cached
    return cache

def cache(func):
    """ビット列キャッシュデコレータ"""

    def cached(self, instance, owner):
        result = func(self, instance, owner)
        setattr(instance, self.name, result)
        return result
    return cached

class mnemonic(object):

    """ビット列表記の親クラス"""

    def __init__(self, length):
        self.length = length
        self.start = lambda instance: 0
        self.name = ''

    @meta_cache('len')
    def real_length(self, instance):
        """ビット列の実際の長さを求める"""

        if isinstance(self.length, int):
            return self.length

        if self.length is None:
            return sum(mnemonic.real_length(instance)
                       for mnemonic in self.cls._mnemonics)
        if isinstance(self.length, mnemonic):
            return getattr(instance, self.length.name) * 8
        if callable(self.length):
            return self.length(instance) * 8
        if isinstance(self.length, str):
            return getattr(instance, self.length) * 8
        return self.length

class uimsbf(mnemonic):

    """unsigned integer most significant bit first[符号無し整数、最上位ビットが先頭]"""

    @cache
    def __get__(self, instance, owner):
        start = self.start(instance)
        length = self.real_length(instance)
        return self.uimsbf(instance._packet, start, length)

    @staticmethod
    def uimsbf(packet, index, length):
        if length == 0:
            return 0

        block = index // 8
        start = index % 8
        pos = 8 - start
        if length + start <= 8:
            shift = pos - length
            filter = 2 ** pos - 2 ** shift
            return (packet[block] & filter) >> shift

        return (uimsbf.uimsbf(packet, index, pos) << (length - pos) |
                uimsbf.uimsbf(packet, index + pos, length - pos))

class bslbf(uimsbf):

    """bit string,left bit first[ビット列、左ビットが先頭]

    実質 uimsbf と同じ処理をすればよい。"""

class rpchof(uimsbf):

    """remainder polynominal coefficients, highest order first[多項式係数の剰余、最上位階数が先頭]

    正しい CRC の値かどうか検証する必要があるが、とりあえず uimsbf と同じ処理とする。"""

class mjd(mnemonic):

    """Modified Julian Date[修正ユリウス日]"""

    @cache
    def __get__(self, instance, owner):
        start = self.start(instance)
        block = start // 8
        last = block + self.real_length(instance) // 8
        pmjd = instance._packet[block:last]
        if pmjd == bytearray(b'\xff\xff\xff\xff\xff'):
            return None
        return datetime(*mjd2datetime(pmjd))

class bcd(mnemonic):

    """二進化十進数で表現された数値"""

    def __init__(self, length, decimal_point=0):
        self.decimal_point = decimal_point
        mnemonic.__init__(self, length)

    @cache
    def __get__(self, instance, owner):
        start = self.start(instance)
        block = start // 8
        last = block + self.real_length(instance) // 8
        pbcd = instance._packet[block:last]
        int_values = map(bcd2int, pbcd)
        value = reduce(lambda x, y: x * 100 + y, int_values)
        return value / (10 ** self.decimal_point)

class bcdtime(mnemonic):

    """二進化十進数で表現された時分秒"""

    @cache
    def __get__(self, instance, owner):
        start = self.start(instance)
        block = start // 8
        last = block + 3
        bcd = instance._packet[block:last]
        if bcd == bytearray(b'\xff\xff\xff'):
            return None
        hour, minute, second = map(bcd2int, bcd)
        return timedelta(hours=hour, minutes=minute, seconds=second)

class otm(mnemonic):

    """オフセット時刻。二進化十進数で表現された時・分・秒・ミリ秒"""

    @cache
    def __get__(self, instance, owner):
        start = self.start(instance)
        block = start // 8
        last = block + 3
        bcd = map(ord, instance._packet[block:last])
        msec = map(ord, instance._packet[last:])
        millisecond = ((msec[0] & 0xF0) >> 4) * 100 + (
                       (msec[0] & 0x0F) * 10) + ((msec[1] & 0x0F) >> 4)
        hour, minute, second = map(bcd2int, bcd)
        return timedelta(hours=hour, minutes=minute, seconds=second,
                         microseconds=millisecond)

class aribstr(mnemonic):

    """8単位符号で符号化された文字列"""

    @cache
    def __get__(self, instance, owner):
        start = self.start(instance)
        block = start // 8
        last = block + self.real_length(instance) // 8
        binary = bytearray(instance._packet[block:last])
        return AribString(binary)

class char(mnemonic):

    """ISO 8859-1に従って8ビットで符号化された文字列"""

    @cache
    def __get__(self, instance, owner):
        start = self.start(instance)
        block = start // 8
        last = block + self.real_length(instance) // 8
        return ''.join(map(chr, instance._packet[block:last]))

class cp932(mnemonic):

    """CP932文字列"""

    @cache
    def __get__(self, instance, owner):
        start = self.start(instance)
        block = start // 8
        last = block + self.real_length(instance) // 8
        return unicode(char(instance._packet, size, cur), 'CP932')

class raw(mnemonic):
    """アレイそのまま"""

    @cache
    def __get__(self, instance, owner):
        start = self.start(instance)
        block = start // 8
        last = block + self.real_length(instance) // 8
        return instance._packet[block:last]

class fixed_size_loop(mnemonic):

    """バイト数固定のループ"""

    def __init__(self, cls, length):
        self.cls = cls
        mnemonic.__init__(self, length)

    @cache
    def __get__(self, instance, owner):
        length = self.real_length(instance) // 8
        start = self.start(instance) // 8
        end = start + length
        result = []
        while start < end:
            start_pos = start * 8
            obj = self.cls(instance._packet, pos=start_pos)
            result.append(obj)
            start += len(obj) // 8
        return result

class fixed_count_loop(mnemonic):

    """回数固定のループ"""

    def __init__(self, cls, count):
        self.cls = cls
        self.count = count
        mnemonic.__init__(self, None)

    @cache
    def __get__(self, instance, owner):
        start = self.start(instance) // 8
        result = []
        for _ in range(self.real_count(instance)):
            start_pos = start * 8
            obj = self.cls(instance._packet, pos=start_pos)
            result.append(obj)
            start += len(obj) // 8
        return result

    @meta_cache('count')
    def real_count(self, instance):
        if isinstance(self.count, int):
            return self.count
        if isinstance(self.count, mnemonic):
            return getattr(instance, self.count.name)
        if callable(self.count):
            return self.count(instance)
        if isinstance(self.count, str):
            return getattr(instance, self.count)
        return self.count

    @meta_cache('len')
    def real_length(self, instance):
        return sum(mnemonic.real_length(sub)
                   for sub in getattr(instance, self.name)
                       for mnemonic in sub._mnemonics)

class case_table(mnemonic):

    """if"""

    def __init__(self, cls, condition):
        self.cls = cls
        self.count = 1
        if isinstance(condition, mnemonic):
            self.condition = lambda instance: getattr(instance, condition.name)
        else:
            self.condition = condition

        mnemonic.__init__(self, None)

    @cache
    def __get__(self, instance, owner):
        if self.condition(instance):
            start_pos = self.start(instance)
            return self.cls(instance._packet, pos=start_pos)
        return None

    @meta_cache('len')
    def real_length(self, instance):
        if self.condition(instance):
            return sum(mnemonic.real_length(instance)
                       for mnemonic in self.cls._mnemonics)
        return 0

def bindump(target):
    """バイナリダンプ"""
    return ' '.join(map(lambda x: format(x, '08b'), target))

def hexdump(target):
    """16進ダンプ"""
    return ' '.join(map(lambda x: format(x, '02X'), target))

def mjd2datetime(pmjd):
    """mjdを年月日時分秒のタプルとして返す
    ARIB-STD-B10第2部付録Cの通りに実装"""

    mjd = (pmjd[0] << 8) | pmjd[1]
    if len(pmjd) > 2:
        bcd = pmjd[2:]
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

def loop(length):
    """サイズ固定のサブシンタックスを返すデコレータ"""

    return lambda cls: fixed_size_loop(cls, length)

def times(count):
    """回数固定のサブシンタックスを返すデコレータ"""

    return lambda cls: fixed_count_loop(cls, count)

def case(condition):
    """ifセクションを返すデコレータ"""

    return lambda cls: case_table(cls, condition)


