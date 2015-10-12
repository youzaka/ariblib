from ariblib.mnemonics import bslbf, mnemonic, uimsbf
from ariblib.syntax import Syntax


class descriptors(mnemonic):

    def __get__(self, instance, owner):
        length = self.real_length(instance) // 8
        start = self.start(instance) // 8
        end = start + length
        while start < end:
            descriptor_tag = instance._packet[start]
            descriptor_length = instance._packet[start + 1] + 2
            block_end = start + descriptor_length
            desc_class = Descriptor.get(descriptor_tag)
            inner = desc_class(instance._packet[start:block_end])
            yield inner
            start = block_end


class Descriptor(Syntax):

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    descriptor = bslbf(descriptor_length)

    @staticmethod
    def get(tag):
        return Descriptor
