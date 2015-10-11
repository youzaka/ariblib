class mnemonic(object):

    def __init__(self, length):
        self.length = length
        self.start = lambda instance: 0
        self.name = ''

    def real_length(self, instance):
        length = self.length
        if isinstance(length, int):
            return length
        if callable(length):
            return length(instance) * 8

    def __sub__(self, other):
        return lambda instance: self.__get__(
            instance, instance.__class__) - other


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


class fixed_size_loop(mnemonic):

    def __init__(self, cls, length):
        self.cls = cls
        mnemonic.__init__(self, length)

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


def loop(length):
    return lambda cls: fixed_size_loop(cls, length)
