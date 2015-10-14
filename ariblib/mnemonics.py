from ariblib.aribstr import AribString


class mnemonic(object):

    def __init__(self, length):
        self.length = length
        self.start = lambda instance: 0
        self.name = ''

    def real_length(self, instance):
        length = self.length
        if isinstance(length, int):
            return length
        if isinstance(length, mnemonic):
            return length.__get__(instance, instance.__class__) * 8
        if callable(length):
            return length(instance) * 8

    def __sub__(self, other):
        if callable(other):
            return lambda instance: self.__get__(
                instance, instance.__class__) - other(instance)
        return lambda instance: self.__get__(
            instance, instance.__class__) - other

    def __add__(self, other):
        if callable(other):
            return lambda instance: self.__get__(
                instance, instance.__class__) + other(instance)
        return lambda instance: self.__get__(
            instance, instance.__class__) + other


class uimsbf(mnemonic):

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
            mask = 2 ** pos - 2 ** shift
            return (packet[block] & mask) >> shift

        shift = length - pos
        return (uimsbf.uimsbf(packet, index, pos) << shift |
                uimsbf.uimsbf(packet, index + pos, shift))


class bslbf(uimsbf):
    pass


class rpchof(uimsbf):
    pass


class aribstr(mnemonic):

    def __get__(self, instance, owner):
        start = self.start(instance)
        block = start // 8
        last = block + self.real_length(instance) // 8
        binary = bytearray(instance._packet[block:last])
        return AribString(binary)


class fixed_size_loop(mnemonic):

    def __init__(self, cls, length):
        self.cls = cls
        mnemonic.__init__(self, length)

    def __get__(self, instance, owner):
        length = self.real_length(instance) // 8
        start = self.start(instance) // 8
        end = start + length
        while start < end:
            start_pos = start * 8
            obj = self.cls(instance._packet, pos=start_pos)
            yield obj
            start += len(obj) // 8


class fixed_count_loop(mnemonic):

    def __init__(self, cls, count):
        self.cls = cls
        self.count = count
        mnemonic.__init__(self, None)

    def __get__(self, instance, owner):
        start = self.start(instance) // 8
        for _ in range(self.real_count(instance)):
            start_pos = start * 8
            obj = self.cls(instance._packet, pos=start_pos)
            yield obj
            start += len(obj) // 8

    def real_count(self, instance):
        count = self.count
        if isinstance(count, int):
            return count
        if isinstance(count, mnemonic):
            return count.__get__(instance, instance.__class__)
        if callable(count):
            return count(instance)
        return self.count

    def real_length(self, instance):
        return sum(mnemonic.real_length(sub)
                   for sub in getattr(instance, self.name)
                   for mnemonic in sub._mnemonics)


def loop(length):
    return lambda cls: fixed_size_loop(cls, length)

def times(count):
    return lambda cls: fixed_count_loop(cls, count)
