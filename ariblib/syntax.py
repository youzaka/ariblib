from ariblib.mnemonics import mnemonic


class SyntaxDict(dict):

    def __init__(self):
        self.mnemonics = []

    def __setitem__(self, key, value):
        if isinstance(value, mnemonic):
            value.name = key
            value.start = self.get_start()
            self.mnemonics.append(value)
        dict.__setitem__(self, key, value)

    def get_start(self):
        mnemonics = self.mnemonics[:]
        return lambda instance: sum(m.real_length(instance) for m in
                                    mnemonics) + instance._pos


class SyntaxType(type):

    @classmethod
    def __prepare__(cls, name, bases):
        return SyntaxDict()

    def __new__(cls, name, args, classdict):
        instance = type.__new__(cls, name, args, classdict)
        instance._mnemonics = classdict.mnemonics
        return instance


class Syntax(metaclass=SyntaxType):

    def __init__(self, packet, pos=0):
        self._packet = packet
        self._pos = pos

    def __len__(self):
        return sum(mnemonic.real_length(self) for mnemonic in self._mnemonics)
