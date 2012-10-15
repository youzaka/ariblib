#!/usr/bin/env python3.2

"""記述子の実装"""

from collections import defaultdict

from ariblib.mnemonics import (aribstr, bslbf, case, char, loop, mjd, mnemonic,
                               raw, times, uimsbf)
from ariblib.syntax import Syntax

class descriptors(mnemonic):

    """記述子リスト"""

    def __get__(self, instance, owner):
        length = self.real_length(instance) // 8
        start = self.start(instance) // 8
        end = start + length
        result = defaultdict(list)
        while start < end:
            descriptor_tag = instance._packet[start]
            descriptor_length = instance._packet[start+1] + 2
            block_end = start + descriptor_length
            desc_class = Descriptor.get(descriptor_tag)
            inner = desc_class(instance._packet[start:block_end])
            result[desc_class].append(inner)
            start = block_end
        return result

class Descriptor(Syntax):

    """記述子の親クラス"""

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    descriptor = bslbf(descriptor_length)

    @staticmethod
    def get(tag):
        return tags.get(tag, Descriptor)


class CAIdentifierDescriptor(Descriptor):

    """CA識別記述子 (ARIB-STD-B10-2-6.2.2)"""

    _tag = 0x09

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)

    @loop(descriptor_length)
    class CAs(Syntax):
        CA_system_id = uimsbf(16)

class CopyrightDescriptor(Descriptor):

    """著作権記述子 (ISO 13818-1 2.6.24)"""

    _tag = 0x0D

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    copyright_identifier = uimsbf(32)
    additional_copyright_info = bslbf(lambda self: self.descriptor_length - 4)

class NetworkNameDescriptor(Descriptor):

    """ネットワーク名記述子(ARIB-STD-B10-2.6.2.11)"""

    _tag = 0x40

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    char = aribstr(descriptor_length)

class ServiceListDescriptor(Descriptor):

    """サービスリスト記述子(ARIB-STD-B10-2-6.2.14)"""

    _tag = 0x41

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)

    @loop(descriptor_length)
    class services(Syntax):
        service_id = uimsbf(16)
        service_type = uimsbf(8)

class ServiceDescriptor(Descriptor):

    """サービス記述子(ARIB-STD-B10-2-6.2.13)"""

    _tag = 0x48

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    service_type = uimsbf(8)
    service_provider_name_length = uimsbf(8)
    service_provider_name = aribstr(service_provider_name_length)
    service_name_length = uimsbf(8)
    service_name = aribstr(service_name_length)

class LinkageDescriptor(Descriptor):

    """リンク記述子(ARIB-STD-B10-2.6.2.8)"""

    _tag = 0x4A

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    transport_stream_id = uimsbf(16)
    original_network_id = uimsbf(16)
    service_id = uimsbf(16)
    linkage_type = uimsbf(8)
    private_data_byte = bslbf(lambda self: self.descriptor_length - 7)

class ShortEventDescriptor(Descriptor):

    """短形式イベント記述子(ARIB-STD-B10-2-6.2.15)"""

    _tag = 0x4D

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    ISO_639_language_code = char(24)
    event_name_length = uimsbf(8)
    event_name_char = aribstr(event_name_length)
    text_length = uimsbf(8)
    text_char = aribstr(text_length)

class ExtendedEventDescriptor(Descriptor):

    """拡張形式イベント記述子(ARIB-STD-B10-2-6.2.7)"""

    _tag = 0x4E

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    descriptor_number = uimsbf(4)
    last_descriptor_number = uimsbf(4)
    ISO_639_language_code = char(24)
    length_of_items = uimsbf(8)

    @loop(lambda self: self.length_of_items)
    class items(Syntax):
        item_description_length = uimsbf(8)
        item_description_char = aribstr(item_description_length)
        item_length = uimsbf(8)
        # マルチバイトの途中でitemが別れていることがあるので、
        # ここでaribstrとしてパースすると文字化けすることがある
        item_char = raw(item_length)

    text_length = uimsbf(8)
    text_char = aribstr(text_length)

class ComponentDescriptor(Descriptor):

    """コンポーネント記述子(ARIB-STD-B10-2-6.2.3)"""

    _tag = 0x50

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    reserved_future_use = bslbf(4)
    stream_content = uimsbf(4)
    component_type = uimsbf(8)
    component_tag = uimsbf(8)
    ISO_639_language_code = char(24)
    component_text = aribstr(lambda self: self.descriptor_length - 6)

class StreamIdentifierDescriptor(Descriptor):

    """ストリーム識別記述子 (ARIB-STD-B10-2-6.2.16)"""

    _tag = 0x52

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    component_tag = uimsbf(8)

class ContentDescriptor(Descriptor):

    """コンテント記述子(ARIB-STD-B10-2-6.2.4)"""

    _tag = 0x54

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)

    @loop(descriptor_length)
    class nibbles(Syntax):
        content_nibble_level_1 = uimsbf(4)
        content_nibble_level_2 = uimsbf(4)
        user_nibble_1 = uimsbf(4)
        user_nibble_2 = uimsbf(4)

class DigitalCopyControlDescriptor(Descriptor):

    """デジタルコピー制御記述子 (ARIB-STD-B10-2-6.2.23)"""

    _tag = 0xC1

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    digital_recording_control_data = bslbf(2)
    maximum_bitrate_flag = bslbf(1)
    component_control_flag = bslbf(1)
    copy_control_type = bslbf(2)

    @case(lambda self: self.copy_control_type == 0b01)
    class with_APS(Syntax):
        APS_control_data = bslbf(2)
    @case(lambda self: self.copy_control_type != 0b01)
    class without_APS(Syntax):
        reserved_future_use = bslbf(2)

    @case(maximum_bitrate_flag)
    class with_maximum_bitrate(Syntax):
        maximum_bitrate = uimsbf(8)

    @case(component_control_flag)
    class with_component_control(Syntax):
        component_control_length = uimsbf(8)

        @loop(component_control_length)
        class components(Syntax):
            component_tag = uimsbf(8)
            digirtal_recording_contorl_data = bslbf(2)
            maximum_bitrate_flag = bslbf(1)
            reserved_future_use = bslbf(1)
            user_defined = bslbf(4)

            @case(maximum_bitrate_flag)
            class with_maximum_bitrate(Syntax):
                maximum_bitrate = uimsbf(8)

class AudioComponentDescriptor(Descriptor):

    """音声コンポーネント記述子(ARIB-STD-B10-2-6.2.26)"""

    _tag = 0xC4

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    reserved_future_use = bslbf(4)
    stream_content = uimsbf(4)
    component_type = uimsbf(8)
    component_tag = uimsbf(8)
    stream_type = uimsbf(8)
    simulcast_group_tag = bslbf(8)
    ES_multi_lingual_flag = bslbf(1)
    main_component_flag = bslbf(1)
    quality_indicator = bslbf(2)
    sampling_rate = uimsbf(3)
    reserved_future_use_2 = bslbf(1)
    ISO_639_language_code = char(24)

    @case(ES_multi_lingual_flag)
    class with_ES_multi_lingual(Syntax):
        ISO_639_language_code_2 = char(24)

    audio_text = aribstr(lambda self:
        self.descriptor_length - 12
        if self.ES_multi_lingual_flag == 1
        else self.descriptor_length - 9)

class HyperLinkDescriptor(Descriptor):

    """ハイパーリンク記述子(ARIB-STD-B10-2.6.2.29)"""

    _tag = 0xC5

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    hyper_linkage_type = uimsbf(8)
    link_destination_type = uimsbf(8)
    selector_length = uimsbf(8)

    @case(lambda self: self.link_destination_type == 0x01)
    class type_01(Syntax):
        original_network_id = uimsbf(16)
        transport_stream_id = uimsbf(16)
        service_id = uimsbf(16)

    @case(lambda self: self.link_destination_type == 0x02)
    class type_02(Syntax):
        original_network_id = uimsbf(16)
        transport_stream_id = uimsbf(16)
        service_id = uimsbf(16)
        event_id = uimsbf(16)

    @case(lambda self: self.link_destination_type == 0x03)
    class type_03(Syntax):
        original_network_id = uimsbf(16)
        transport_stream_id = uimsbf(16)
        service_id = uimsbf(16)
        event_id = uimsbf(16)
        component_tag = uimsbf(8)
        module_id = uimsbf(16)

    @case(lambda self: self.link_destination_type == 0x04)
    class type_04(Syntax):
        original_network_id = uimsbf(16)
        transport_stream_id = uimsbf(16)
        service_id = uimsbf(16)
        content_id = uimsbf(32)

    @case(lambda self: self.link_destination_type == 0x05)
    class type_05(Syntax):
        original_network_id = uimsbf(16)
        transport_stream_id = uimsbf(16)
        service_id = uimsbf(16)
        content_id = uimsbf(32)
        component_tag = uimsbf(8)
        module_id = uimsbf(16)

    @case(lambda self: self.link_destination_type == 0x06)
    class type_06(Syntax):
        information_provide_id = uimsbf(16)
        event_relation_id = uimsbf(16)
        node_id = uimsbf(16)

    @case(lambda self: self.link_destination_type == 0x07)
    class type_07(Syntax):
        uri_char = char(lambda self: self.selector_length)

class DataContentDescriptor(Descriptor):

    """データコンテンツ記述子(ARIB-STD-B10-2-6.2.28)

    data_component_idが0x0008のものは、selector_byteに
    字幕・文字スーパーの識別情報が入っている(ARIB-STD-B24-1-3-9.6.2)

    """
    _tag = 0xC7

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    data_component_id = uimsbf(16)
    entry_component = uimsbf(8)
    selector_length = uimsbf(8)
    selector_byte = uimsbf(selector_length)
    num_of_component_ref = uimsbf(8)

    @times(num_of_component_ref)
    class component_refs(Syntax):
        component_ref = uimsbf(8)

    ISO_639_language_code = char(24)
    text_length = uimsbf(8)
    data_text = aribstr(text_length)

class VideoDecodeControlDescriptor(Descriptor):

    """ビデオデコードコントロール記述子 (ARIB-STD-B10-2-6.2.30)"""

    _tag = 0xC8

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    still_picture_flag = bslbf(1)
    sequence_end_code_flag = bslbf(1)
    video_encode_format = bslbf(4)
    reserved_future_use = bslbf(2)

class EncryptDescriptor(Descriptor):

    """Encrypt記述子(ARIB-STD-B15-3.4.4.7)"""

    _tag = 0xCB

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    encrypt_id = uimsbf(8)

class TSInformationDescriptor(Descriptor):

    """TS情報記述子(ARIB-STD-B10-2.6.2.42)"""

    _tag = 0xCD

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

class ExtendedBroadcasterDescriptor(Descriptor):

    """拡張ブロードキャスタ記述子(ARIB-STD-B10-2-6.2.43)"""

    _tag = 0xCF

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    broadcaster_type = uimsbf(4)
    reserved_future_use = bslbf(4)

    @case(lambda self: self.broadcaster_type == 0x1)
    class type_1(Syntax):
        terrestrial_broadcaster_id = uimsbf(16)
        number_of_affiliation_id_loop = uimsbf(4)
        number_of_broadcaster_id_loop = uimsbf(4)

        @times(number_of_affiliation_id_loop)
        class affiliations(Syntax):
            affiliation_id = uimsbf(8)

        @times(number_of_broadcaster_id_loop)
        class broadcasters(Syntax):
            original_network_id = uimsbf(8)
            broadcaster_id = uimsbf(8)

        private_data_byte = bslbf(lambda self:
            self.descriptor_length - (
                4 + self.number_of_affiliation_id_loop +
                self.number_of_broadcaster_id_loop * 3))

    @case(lambda self: self.broadcaster_type == 0x2)
    class type_2(Syntax):
        terrestrial_sound_broadcaster_id = uimsbf(16)
        number_of_sound_broadcast_affiliation_id_loop = uimsbf(4)
        number_of_broadcaster_id_loop = uimsbf(4)

        @times(number_of_sound_broadcast_affiliation_id_loop)
        class sound_broadcast_affiliations(Syntax):
            sound_broadcast_affiliations_id = uimsbf(8)

        @times(number_of_broadcaster_id_loop)
        class broadcasters(Syntax):
            original_network_id = uimsbf(8)
            broadcaster_id = uimsbf(8)

        private_data_byte = bslbf(lambda self:
            self.descriptor_length - (
                4 + self.number_of_sound_broadcast_affiliation_id_loop +
                self.number_of_broadcaster_id_loop * 3))

    @case(lambda self: self.broadcaster_type not in (0x1, 0x2))
    class type_other(Syntax):
        reserved_future_use = bslbf(lambda self: self.description_length -1)

class LogoTransmissionDescriptor(Descriptor):

    """ロゴ伝送記述子(ARIB-STD-B10-2-6.2.44)"""

    _tag = 0xCF

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    logo_transmission_type = uimsbf(8)

    @case(lambda self: self.logo_transmission_type == 0x01)
    class type_01(Syntax):
        reserved_future_use_1 = bslbf(7)
        logo_id = uimsbf(9)
        reserved_future_use_2 = bslbf(4)
        logo_version = uimsbf(12)
        download_data_id = uimsbf(16)

    @case(lambda self: self.logo_transmission_type == 0x02)
    class type_02(Syntax):
        reserved_future_use_1 = bslbf(7)
        logo_id = uimsbf(9)

    @case(lambda self: self.logo_transmission_type == 0x03)
    class type_03(Syntax):
        logo_char = aribstr(lambda self: self.descriptor_length - 1)

    reserved_future_use = bslbf(lambda self: self.descriptor_length - 1)

class EventGroupDescriptor(Descriptor):

    """イベントグループ記述子 (ARIB-STD-B10-2-6.2.34)"""

    _tag = 0xD6

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    group_type = uimsbf(4)
    event_count = uimsbf(4)

    @times(event_count)
    class events(Syntax):
        service_id = uimsbf(16)
        event_id = uimsbf(16)

    @case(lambda self: self.group_type in (4, 5))
    class with_network(Syntax):
        @times(lambda self: self.event_count)
        class networks(Syntax):
            original_network_id = uimsbf(16)
            transport_stream_id = uimsbf(16)
            service_id = uimsbf(16)
            event_id = uimsbf(16)

    @case(lambda self: self.group_type not in (4, 5))
    class without_network(Syntax):
        private_data_byte = aribstr(lambda self:
            self.descriptor_length - 1 - self.event_count * 4)

class SIParameterDescriptor(Descriptor):

    """SI伝送パラメータ記述子(ARIB-STD-B10-2-6.2.35)"""

    _tag = 0xD7

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    parameter_version = uimsbf(8)
    update_time = mjd(16)

    @loop(lambda self: self.descriptor_length - 3)
    class parameters(Syntax):
        table_id = uimsbf(8)
        table_description_length = uimsbf(8)

        @loop(lambda self: self.table_description_length)
        class descriptions(Syntax):
            table_description_byte = uimsbf(8)

class ContentAvailabilityDescriptor(Descriptor):

    """コンテント利用記述子 (ARIB-STD-B10-2-6.2.45)"""

    _tag = 0xDE

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    reserved_future_use_1 = bslbf(1)
    copy_restriction_mode = bslbf(1)
    image_constraint_token = bslbf(1)
    retention_mode = bslbf(1)
    retention_state = bslbf(3)
    encryption_mode = bslbf(1)
    reserved_future_use_2 = bslbf(lambda self: self.descriptor_length - 1)

class AccessControlDescriptor(Descriptor):

    """アクセス制御記述子 (ARIB-TR-B14 第四篇改定案 30.2.2.2"""

    _tag = 0xF6

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    CA_system_ID = uimsbf(16)
    transmission_type = bslbf(3)
    PID = uimsbf(13)
    private_data_byte = bslbf(lambda self: self.descriptor_length - 4)

class TerrestrialDeliverySystemDescriptor(Descriptor):

    """地上分配システム記述子(ARIB-STD-B10-2-6.2.31)"""

    _tag = 0xFA

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    area_code = bslbf(12)
    guard_interval = bslbf(2)
    transmission_mode = bslbf(2)

    @loop(lambda self: self.descriptor_length - 2)
    class freqs(Syntax):
        frequency = uimsbf(16)

class PartialReceptionDescriptor(Descriptor):

    """部分受信記述子(ARIB-STD-B10-2.6.2.32)"""

    _tag = 0xFB

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)

    @loop(descriptor_length)
    class services(Syntax):
        service_id = uimsbf(16)

class DataComponentDescriptor(Descriptor):

    """データ符号化方式記述子(ARIB-STD-B10-2-6.2.20)

    data_component_idが0x0008のものは、additional_data_component_infoに
    字幕・文字スーパーの識別情報が入っている(ARIB-STD-B24-1-3-9.6.1)

    """

    _tag = 0xFD

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    data_component_id = uimsbf(16)

    @case(lambda self: self.data_component_id == 0x07)
    class component_07(Syntax):
        transmission_format = bslbf(2)
        entry_point_flag = bslbf(1)

        @case(entry_point_flag)
        class with_entry_point(Syntax):
            auto_start_flag = bslbf(1)
            document_resolution = bslbf(4)
            use_xml = bslbf(1)
            default_version_flag = bslbf(1)
            independent_flag = bslbf(1)
            style_for_tv_flag = bslbf(1)
            reserved_future_use_1 = bslbf(4)

            @case(default_version_flag)
            class with_default_version(Syntax):
                bml_major_version = uimsbf(16)
                bml_minor_version = uimsbf(16)

                @case(lambda self: self.use_xml)
                class with_xml(Syntax):
                    bxml_major_version = uimsbf(16)
                    bxml_minor_version = uimsbf(16)

        @case(lambda self: not self.entry_point_flag)
        class without_entry_point(Syntax):
            reserved_future_use_2 = bslbf(5)

        @case(lambda self: self.transmission_format == 0b00)
        class transmission_00(Syntax):
            # additional_arib_carousel_info (ARIB-STD-B24-3-C.1
            data_event_id = uimsbf(4)
            event_section_flag = bslbf(1)
            reserved = bslbf(3)
            ondemand_retrieval_flag = bslbf(1)
            file_storable_flag = bslbf(1)
            reserved_future_use_3 = bslbf(6)

        @case(lambda self: self.transmission_format == 0b01)
        class transmission_01(Syntax):
            reserved_future_use_4 = bslbf(8)

    @case(lambda self: self.data_component_id == 0x08)
    class component_08(Syntax):
        DMF = bslbf(4)
        reserved = bslbf(2)
        timing = bslbf(2)

    @case(lambda self: self.data_component_id not in (0x07, 0x08))
    class default_component(Syntax):
        additional_data_component_info = uimsbf(lambda self: self.descriptor_length - 2)

class SystemManagementDescriptor(Descriptor):

    """システム管理記述子(ARIB-STD-B10-2-6.2.21)"""

    _tag = 0xFE

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    system_management_id = uimsbf(16)
    additional_identification_info = uimsbf(lambda self: self.descriptor_length - 2)

#FIXME: わざわざこの辞書を明示したくない
tags = {
    0x09: CAIdentifierDescriptor,
    0x0D: CopyrightDescriptor,
    0x40: NetworkNameDescriptor,
    0x41: ServiceListDescriptor,
    0x48: ServiceDescriptor,
    0x4A: LinkageDescriptor,
    0x4D: ShortEventDescriptor,
    0x4E: ExtendedEventDescriptor,
    0x50: ComponentDescriptor,
    0x52: StreamIdentifierDescriptor,
    0x54: ContentDescriptor,
    0xC1: DigitalCopyControlDescriptor,
    0xC4: AudioComponentDescriptor,
    0xC5: HyperLinkDescriptor,
    0xC7: DataContentDescriptor,
    0xC8: VideoDecodeControlDescriptor,
    0xCB: EncryptDescriptor,
    0xCD: TSInformationDescriptor,
    0xCE: ExtendedBroadcasterDescriptor,
    0xCF: LogoTransmissionDescriptor,
    0xD6: EventGroupDescriptor,
    0xD7: SIParameterDescriptor,
    0xDE: ContentAvailabilityDescriptor,
    0xF6: AccessControlDescriptor,
    0xFA: TerrestrialDeliverySystemDescriptor,
    0XFB: PartialReceptionDescriptor,
    0xFD: DataComponentDescriptor,
    0xFE: SystemManagementDescriptor,
}

