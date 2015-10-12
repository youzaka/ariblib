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


tags = {}


def tag(tag_id):
    def wrapper(cls):
        cls._tag = tag_id
        tags[tag_id] = cls
        return cls
    return wrapper


class Descriptor(Syntax):

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    descriptor = bslbf(descriptor_length)

    @staticmethod
    def get(tag):
        return tags.get(tag, Descriptor)


@tag(0x09)
class ConditionalAccessDescriptor(Descriptor):

    """限定受信方式記述子 (ARIB-TR-B14-4.3.2.2.1, ARIB-TR-B15-4.3.2.2.1)"""

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    CA_system_ID = uimsbf(16)
    reserved = bslbf(3)
    CA_PID = uimsbf(13)
    private_data_bytes = bslbf(descriptor_length - 4)


@tag(0x52)
class StreamIdentifierDescriptor(Descriptor):

    """ストリーム識別記述子 (ARIB-STD-B10-2.6.2.16)"""

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    component_tag = uimsbf(8)


@tag(0xC1)
class DigitalCopyControlDescriptor(Descriptor):

    """デジタルコピー制御記述子 (ARIB-STD-B10-2.6.2.23)"""

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    digital_recording_control_data = bslbf(2)
    maximum_bitrate_flag = bslbf(1)
    component_control_flag = bslbf(1)
    copy_control_type = bslbf(2)
    APS_control_data = bslbf(2)


@tag(0xC8)
class VideoDecodeControlDescriptor(Descriptor):

    """ビデオでコードコントロール記述子 (ARIB-STD-B10-2.6.2.30)"""

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    still_picture_flag = bslbf(1)
    sequence_end_code_flag = bslbf(1)
    video_encode_format = bslbf(4)
    reserved_future_use = bslbf(2)


@tag(0xFD)
class DataComponentDescriptor(Descriptor):

    """データ符号化記述子 (ARIB-STD-B10-2.6.2.10)"""

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    data_component_id = uimsbf(16)
    additional_data_component_info = uimsbf(descriptor_length - 2)
