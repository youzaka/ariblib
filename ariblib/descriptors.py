from ariblib.mnemonics import aribstr, bslbf, loop, mnemonic, times, uimsbf
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


@tag(0x40)
class NetworkNameDescriptor(Descriptor):

    """ネットワーク名記述子(ARIB-STD-B10-2.6.2.11)"""

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    char = aribstr(descriptor_length)


@tag(0x41)
class ServiceListDescriptor(Descriptor):

    """サービスリスト記述子(ARIB-STD-B10-2-6.2.14)"""

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)

    @loop(descriptor_length)
    class services(Syntax):
        service_id = uimsbf(16)
        service_type = uimsbf(8)


@tag(0x48)
class ServiceDescriptor(Descriptor):

    """サービス記述子(ARIB-STD-B10-2-6.2.13)"""

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    service_type = uimsbf(8)
    service_provider_name_length = uimsbf(8)
    service_provider_name = aribstr(service_provider_name_length)
    service_name_length = uimsbf(8)
    service_name = aribstr(service_name_length)


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


@tag(0xCD)
class TSInformationDescriptor(Descriptor):

    """TS情報記述子(ARIB-STD-B10-2.6.2.42)"""

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    remote_control_key_id = uimsbf(8)
    length_of_ts_name = uimsbf(6)
    transmission_type_count = uimsbf(2)
    ts_name_char = aribstr(length_of_ts_name)

    @times(transmission_type_count)
    class transmissions(Syntax):
        transmission_type_info = bslbf(8)
        num_of_service = uimsbf(8)

        @times(num_of_service)
        class services(Syntax):
            service_id = uimsbf(16)


@tag(0xFA)
class TerrestrialDeliverySystemDescriptor(Descriptor):

    """地上分配システム記述子(ARIB-STD-B10-2-6.2.31)"""

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    area_code = bslbf(12)
    guard_interval = bslbf(2)
    transmission_mode = bslbf(2)

    @loop(descriptor_length - 2)
    class freqs(Syntax):
        frequency = uimsbf(16)


@tag(0xFB)
class PartialReceptionDescriptor(Descriptor):

    """部分受信記述子(ARIB-STD-B10-2.6.2.32)"""

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)

    @loop(descriptor_length)
    class services(Syntax):
        service_id = uimsbf(16)


@tag(0xFD)
class DataComponentDescriptor(Descriptor):

    """データ符号化記述子 (ARIB-STD-B10-2.6.2.10)"""

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    data_component_id = uimsbf(16)
    additional_data_component_info = uimsbf(descriptor_length - 2)


@tag(0xFE)
class SystemManagementDescriptor(Descriptor):

    """システム管理記述子(ARIB-STD-B10-2-6.2.21, ARIB-TR-B14-30.4.2.2)"""

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    broadcasting_flag = uimsbf(2)  # 放送 0x00
    broadcasting_identifier = uimsbf(6)  # 地デジ 0x03, BS 0x02, CS 0x04
    additional_broadcasting_identification = uimsbf(8)  # 0x01
    additional_identification_info = uimsbf(descriptor_length - 2)
