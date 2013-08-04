#!/usr/bin/env python3.2

"""記述子の実装"""

from collections import defaultdict

from ariblib.mnemonics import (aribstr, bcd, bslbf, cache, case, char, loop,
                               mjd, mnemonic, raw, times, uimsbf)
from ariblib.syntax import Syntax

class descriptors(mnemonic):

    """記述子リスト"""

    @cache
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

class SatelliteDeliverySystemDescriptor(Descriptor):

    """衛星分配システム記述子(ARIB-STD-B10-2-6.2.6)"""

    _tag = 0x43

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    frequency = bcd(32, 6)
    orbital_position = bcd(16, 1)
    west_east_flag = bslbf(1)
    polarisation = bslbf(2)
    modulation = bslbf(5)
    symbol_rate = bcd(28, 5)
    FEC_inner = bslbf(4)

class BouquetNameDescriptor(Descriptor):

    """ブーケ名記述子(ARIB-STD-B10-2.6.2.1)"""

    _tag = 0x47

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    char = aribstr(descriptor_length)

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

class CountryAvailabilityDescriptor(Descriptor):

    """国別受信可否記述子(ARIB-STD-B10-2.6.2.5)"""

    _tag = 0x49

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    country_availability_flag = bslbf(1)
    reserved_future_use = bslbf(7)

    @loop(lambda self: self.descriptor_length - 1)
    class countries(Syntax):
        country_code = char(24)

class LinkageDescriptor(Descriptor):

    """リンク記述子(ARIB-STD-B10-2.6.2.8)"""

    _tag = 0x4A

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    transport_stream_id = uimsbf(16)
    original_network_id = uimsbf(16)
    service_id = uimsbf(16)
    linkage_type = uimsbf(8)

    @case(lambda self: self.linkage_type == 0x0B)
    class linkage_type_0x0B(Syntax):
        platform_id_data_length = uimsbf(8)

        @loop(platform_id_data_length)
        class platforms(Syntax):
            platform_id = uimsbf(24)
            platform_name_loop_length = uimsbf(8)

            @loop(platform_name_loop_length)
            class names(Syntax):
                ISO_639_language_code = char(24)
                platform_name_length = uimsbf(8)
                text_char = aribstr(platform_name_length)

    @case(lambda self: self.linkage_type == 0x03)
    class linkage_type_0x03(Syntax):
        message_id = uimsbf(8)
        message = aribstr(lambda self: self.descriptor_length - 8)

    @case(lambda self: self.linkage_type not in (0x03, 0x0B))
    class default(Syntax):
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
        user_nibble = uimsbf(8)

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

    # ARIB-STD-B24-1-3-9.6.2
    # これ以外のselector_byteの実装は、ifの入れ子が正しく処理できないと実装できない
    @case(lambda self: self.data_component_id == 0x08)
    class arib_caption_info(Syntax):
        num_languages = uimsbf(8)

        @times(num_languages)
        class languages(Syntax):
            language_tag = bslbf(3)
            reserved = bslbf(1)
            DMF = bslbf(4)
            ISO_639_language_code = char(24)

    @case(lambda self: self.data_component_id != 0x08)
    class other(Syntax):
        selector_byte = uimsbf(lambda self: self.selector_length)

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

class DownloadContentDescriptor(Descriptor):

    """ダウンロードコンテンツ記述子(ARIB-STD-B21-12.2.1.1)"""

    _tag = 0xC9

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    reboot = bslbf(1)
    add_on = bslbf(1)
    compatibility_flag = bslbf(1)
    module_info_flag = bslbf(1)
    text_info_flag = bslbf(1)
    reserved_1 = bslbf(3)
    component_size = uimsbf(32)
    download_id = uimsbf(32)
    time_out_value_DII = uimsbf(32)
    leak_rate = uimsbf(22)
    reserved_2 = bslbf(2)
    component_tag = uimsbf(8)

    @case(compatibility_flag)
    class CompatibilityDescriptor(Syntax):
        """Compatibility Descriptor (ARIB-STD-B21-12.2.2.1)"""

        compatibility_descriptor_length = uimsbf(16)
        descriptor_count = uimsbf(16)

        @times(descriptor_count)
        class compatibility_descriptors(Syntax):
            descriptor_type = uimsbf(8)
            descriptor_length = uimsbf(8)
            specifier_type = uimsbf(8)
            specifier_data = bslbf(24)
            model = uimsbf(16)
            version = uimsbf(16)
            sub_descriptor_count = uimsbf(8)

            @times(sub_descriptor_count)
            class sub_descriptors(Syntax):
                sub_descriptor_type = uimsbf(8)
                sub_descriptor_length = uimsbf(8)
                additional_information = uimsbf(sub_descriptor_length)

    @case(module_info_flag)
    class ModuleInfo(Syntax):
        num_of_modules = uimsbf(16)

        @times(num_of_modules)
        class modules(Syntax):
            module_id = uimsbf(16)
            module_size = uimsbf(32)
            module_info_length = uimsbf(8)
            module_info_byte = uimsbf(module_info_length)

    private_data_length = uimsbf(8)
    private_date_byte = uimsbf(private_data_length)

    @case(text_info_flag)
    class TextInfo(Syntax):
        ISO_639_language_code = char(24)
        text_length = uimsbf(8)
        text_char = aribstr(text_length)

class EncryptDescriptor(Descriptor):

    """Encrypt記述子(ARIB-STD-B25-3.4.4.7)"""

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

    @case(lambda self: self.logo_transmission_type not in (0x01, 0x02, 0x03))
    class type_else(Syntax):
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
    parameter_version = uimsbf(8) # 地デジ 0xFF
    update_time = mjd(16)

    @loop(lambda self: self.descriptor_length - 3)
    class parameters(Syntax):
        table_id = uimsbf(8)
        table_description_length = uimsbf(8)

        # ARIB-TR-B14-31.1.2.1, ARIB-TR-B15-31.2.2.1
        @case(lambda self: self.table_id in
            (0x40, 0x42, 0x46, 0x4E, 0x4F, 0xC4)
            and self.table_description_length == 1)
        class table_description_1_1(Syntax):
            table_cycle = bcd(8)

        @case(lambda self: self.table_id in (0xC3, 0xC8))
        class table_description_1_2(Syntax):
            table_cycle = bcd(16)

        @case(lambda self: self.table_id == 0x4E and
                           self.table_description_length == 4)
        class table_description_2(Syntax):
            table_cycle_H_EIT_PF = bcd(8)
            table_cycle_M_EIT = bcd(8)
            table_cycle_L_EIT = bcd(8)
            num_of_M_EIT_event = uimsbf(4)
            num_of_L_EIT_event = uimsbf(4)

        @case(lambda self: self.table_id in (0x50, 0x58, 0x60))
        class table_description_3(Syntax):
            @loop(lambda self: self.table_description_length)
            class cycles(Syntax):
                media_type = uimsbf(2)
                pattern = uimsbf(2)
                reserved_1 = bslbf(4)
                schdule_range = bcd(8)
                base_cycle = bcd(12)
                reserved_2 = bslbf(2)
                cycle_group_count = uimsbf(2)

                @times(cycle_group_count)
                class groups(Syntax):
                    num_of_segment = bcd(8)
                    cycle = bcd(8)

        @case(lambda self: self.table_id not in(
            0x40, 0x42, 0x46, 0x4E, 0x4F, 0x50, 0x58, 0x60, 0xC3, 0xC4, 0xC8))
        class table_description_else(Syntax):
            table_description_byte = bslbf(lambda self: self.table_description_length)


class BroadcasterNameDescriptor(Descriptor):

    """ブロードキャスタ名記述子(ARIB-STD-B10-2-6.2.36)"""

    _tag = 0xD8

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    char = aribstr(descriptor_length)


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

    """システム管理記述子(ARIB-STD-B10-2-6.2.21, ARIB-TR-B14-30.4.2.2)"""

    _tag = 0xFE

    descriptor_tag = uimsbf(8)
    descriptor_length = uimsbf(8)
    broadcasting_flag = uimsbf(2) # 放送 0x00
    broadcasting_identifier = uimsbf(6) # 地デジ 0x03, BS 0x02, CS 0x04
    additional_broadcasting_identification = uimsbf(8) # 0x01
    additional_identification_info = uimsbf(lambda self: self.descriptor_length - 2)

#FIXME: わざわざこの辞書を明示したくない
tags = {
    #0x05: 登録記述子
    0x09: CAIdentifierDescriptor,
    0x0D: CopyrightDescriptor,
    #0x13: カルーセル識別記述子
    #0x14: アソシエーションタグ記述子,
    #0x15: 拡張アソシエーションタグ記述子
    #0x1C: MPEG-4 オーディオ記述子,
    #0x28: AVCビデオ記述子,
    #0x2A: AVCタイミングHRD記述子,
    #0x2E: MPEG-4オーディオ拡張記述子,
    0x40: NetworkNameDescriptor,
    0x41: ServiceListDescriptor,
    #0x42: スタッフ記述子,
    0x43: SatelliteDeliverySystemDescriptor,
    #0x44: 優先分配システム記述子,
    0x47: BouquetNameDescriptor,
    0x48: ServiceDescriptor,
    0x49: CountryAvailabilityDescriptor,
    0x4A: LinkageDescriptor,
    #0x4B: NVOD基準サービス記述子,
    #0x4C: タイムシフトサービス記述子,
    0x4D: ShortEventDescriptor,
    0x4E: ExtendedEventDescriptor,
    0x50: ComponentDescriptor,
    #0x51: モザイク記述子,
    0x52: StreamIdentifierDescriptor,
    #0x53: CA識別記述子,
    0x54: ContentDescriptor,
    #0x55: パレンタルレート記述子,
    #0x58: ローカル時間オフセット記述子,
    #0x63: パーシャルトランスポートストリーム識別子,
    #0x66: データブロードキャスト識別記述子,
    #0xC0: 階層伝送記述子,
    0xC1: DigitalCopyControlDescriptor,
    #0xC2: ネットワーク識別記述子,
    #0xC3: パーシャルトランスポートストリームタイム記述子,
    0xC4: AudioComponentDescriptor,
    0xC5: HyperLinkDescriptor,
    #0xC6: 対象地域記述子,
    0xC7: DataContentDescriptor,
    0xC8: VideoDecodeControlDescriptor,
    0xCB: EncryptDescriptor,
    0xC9: DownloadContentDescriptor,
    #0xCA: CA_EMM_TS記述子,
    #0xCB: CA契約情報記述子,
    #0xCC: CAサービス記述子,
    0xCD: TSInformationDescriptor,
    0xCE: ExtendedBroadcasterDescriptor,
    0xCF: LogoTransmissionDescriptor,
    #0xD0: 基本ローカルイベント記述子,
    #0xD1: リファレンス記述子,
    #0xD2: ノード関係記述子,
    #0xD3: 短形式ノード情報記述子,
    #0xD4: STC参照記述子,
    #0xD5: シリーズ記述子,
    0xD6: EventGroupDescriptor,
    0xD7: SIParameterDescriptor,
    0xD8: BroadcasterNameDescriptor,
    #0xD9: コンポーネントグループ記述子,
    #0xDA: SIプライムTS記述子,
    #0xDB: 掲示板情報記述子,
    #0xDC: LDTリンク記述子,
    #0xDD: 連結送信記述子,
    0xDE: ContentAvailabilityDescriptor,
    #0xE0: サービスグループ記述子,
    0xF6: AccessControlDescriptor,
    #0xF7: カルーセル互換複合記述子,
    #0xF8: 限定再生方式記述子,
    #0xF9: 有線TS分割システム記述子,
    0xFA: TerrestrialDeliverySystemDescriptor,
    0xFB: PartialReceptionDescriptor,
    #0xFC: 緊急情報記述子,
    0xFD: DataComponentDescriptor,
    0xFE: SystemManagementDescriptor,
}

