"""DII記述子の実装"""

from collections import defaultdict

from ariblib.mnemonics import (
    aribstr,
    bcd,
    bslbf,
    cache,
    case,
    char,
    loop,
    mjd,
    mnemonic,
    raw,
    rpchof,
    times,
    uimsbf
)
from ariblib.syntax import Syntax

tags = {}


def tag(tag_id):
    def wrapper(cls):
        cls._tag = tag_id
        tags[tag_id] = cls
        return cls
    return wrapper


class diidescriptors(mnemonic):

    """DII記述子リスト"""

    @cache
    def __get__(self, instance, owner):
        length = self.real_length(instance) // 8
        start = self.start(instance) // 8
        end = start + length
        result = defaultdict(list)
        while start < end:
            descriptor_tag = instance._packet[start]
            descriptor_length = instance._packet[start + 1] + 2
            block_end = start + descriptor_length
            desc_class = diiDescriptor.get(descriptor_tag)
            inner = desc_class(instance._packet[start:block_end])
            result[desc_class].append(inner)
            start = block_end
        return result


class diiDescriptor(Syntax):

    """DII記述子の親クラス"""

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    descriptor = bslbf(descriptor_length)

    @staticmethod
    def get(tag):
        return tags.get(tag, diiDescriptor)


@tag(0x01)
class Type_descriptor(diiDescriptor):
    """Type 記述子 (ARIB-STD-B24-3-6.2.3.1　表6-5)"""
    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    text = char(lambda self: self.descriptor_length)


@tag(0x02)
class Name_descriptor(diiDescriptor):
    """Name 記述子 (ARIB-STD-B24-3-6.2.3.2　表6-6)"""
    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    text = char(descriptor_length)


@tag(0x03)
class info_descriptor(diiDescriptor):
    """Info 記述子 (ARIB-STD-B24-3-6.2.3.3　表6-7)"""
    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    ISO_639_language_code = char(24)
    text_char = aribstr(descriptor_length)


@tag(0x04)
class module_link_descriptor(diiDescriptor):
    """Module_Link 記述子 (ARIB-STD-B24-3-6.2.3.4　表6-8)"""
    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    position = uimsbf(8)
    moduleId = uimsbf(16)


@tag(0x05)
class CRC32_descriptor(diiDescriptor):
    """CRC 記述子 (ARIB-STD-B24-3-6.2.3.5　表6-9)"""
    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    CRC_32 = rpchof(32)


@tag(0x07)
class est_download_time_descriptor(diiDescriptor):
    """ダウンロード推定時間記述子 (ARIB-STD-B24-3-6.2.3.6　表6-10)"""
    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    est_download_time = uimsbf(32)


@tag(0xC0)
class Expire_descriptor(diiDescriptor):
    """Expire 記述子 (ARIB-STD-B24-3-6.2.3.7　表6-11)"""
    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    time_mode = uimsbf(8)

    @case(lambda self: self.time_mode == 0x01)
    class time_mode_0x01(Syntax):
        MJD_JST_time = mjd(40)

    @case(lambda self: self.time_mode == 0x04)
    class time_mode_0x04(Syntax):
        reserved_future_use = bslbf(8)
        passed_seconds = uimsbf(32)


@tag(0xC1)
class Activation_Time_descriptor(diiDescriptor):
    """ActivationTime 記述子 (ARIB-STD-B24-3-6.2.3.8　表6-12)"""
    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    time_mode = uimsbf(8)

    @case(lambda self: self.time_mode == 0x01)
    class time_mode_0x01(Syntax):
        MJD_JST_time = mjd(40)

    @case(lambda self: self.time_mode == 0x05)
    class time_mode_0x05(Syntax):
        MJD_JST_time = mjd(40)

    @case(lambda self: self.time_mode == 0x02)
    class time_mode_0x02(Syntax):
        reserved_future_use = bslbf(7)
        NPT_time = uimsbf(33)

    @case(lambda self: self.time_mode == 0x03)
    class time_mode_0x03(Syntax):
        reserved_future_use = bslbf(4)
        NPT_time = bslbf(36)


@tag(0xC2)
class Compression_Type_descriptor(diiDescriptor):
    """CompressionType 記述子 (ARIB-STD-B24-3-6.2.3.9　表6-13)"""
    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    compression_type = uimsbf(8)
    original_size = uimsbf(32)


@tag(0xC3)
class Control_descriptor(diiDescriptor):
    """Control 記述子 (ARIB-STD-B24-3-6.2.3.10　表6-14)"""
    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)

    @loop(lambda self: self.descriptor_length)
    class control_data_bytes(Syntax):
        control_data_byte = bslbf(8)


@tag(0xC4)
class Provider_Private_descriptor(diiDescriptor):
    """ProviderPrivate 記述子 (ARIB-STD-B24-3-6.2.3.11　表6-15)

    FIXME: private_scope_typeに対応するすべての識別子の処理の実装
    """
    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    private_scope_type = bslbf(8)
    scope_identifier = bslbf(32)

    @loop(lambda self: self.descriptor_length-5)  # 32 bit + 8 bit / 8
    class private_bytes(Syntax):
        private_byte = bslbf(8)


@tag(0xC5)
class store_root_descriptor(diiDescriptor):
    """StoreRoot 記述子(ARIB-STD-B24-3-6.2.3.12　表6-16)"""
    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    update_type = bslbf(1)
    reserved = bslbf(7)

    store_root_path = char(lambda self: self.descriptor_length-1)


@tag(0xC6)
class subdirectory_descriptor(diiDescriptor):
    """Subdirectory 記述子 (ARIB-STD-B24-3-6.2.3.13　表6-17)"""
    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    subdirectory_path = char(descriptor_length)


@tag(0xC7)
class title_descriptor(diiDescriptor):
    """Title 記述子 (ARIB-STD-B24-3-6.2.3.14　表6-18)"""
    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    ISO_639_language_code = bslbf(24)
    text_char = aribstr(lambda self: self.descriptor_length-3)


@tag(0xC8)
class data_encoding_descriptor(diiDescriptor):
    """DataEncoding 記述子(ARIB-STD-B24-3-6.2.3.15　表6-19)"""
    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    data_compoent_id = uimsbf(16)
    additional_data_encoding_info = raw(
        lambda self: self.descriptor_length-2)  # 16 bit / 2


@tag(0xCA)
class root_cetificate_descriptor(diiDescriptor):
    """ルート証明書記述子 (ARIB-STD-B24-3-6.2.3.16　表6-20)"""
    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    root_certificate_type = bslbf(1)
    reserved = bslbf(7)

    @case(lambda self: self.root_certificate_type == 0)
    @loop(lambda self: self.descriptor_length - 1)
    class root_certificate_type_0(Syntax):
        root_certificate_id = uimsbf(32)
        root_certificate_version = uimsbf(32)

    @case(lambda self: self.root_certificate_type != 0)
    @loop(lambda self: self.descriptor_length - 1)
    class root_certificate_type_not_0(Syntax):
        reserved = bslbf(64)
