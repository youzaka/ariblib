#!/usr/bin/env python3.2

"""各種 PSI セクションの定義"""

from collections import defaultdict
from datetime import datetime, timedelta

from ariblib.aribstr import AribString
from ariblib.descriptors import descriptors
from ariblib.mnemonics import bcd, bslbf, loop, rpchof, mjd, uimsbf
from ariblib.syntax import Syntax

class Section(Syntax):

    """セクションの親クラス

    PSI はこれの子クラスとする。字幕 PES も便宜的にそうする
    """

    _table_ids = range(256)

    def __getattr__(self, name):
        result = Syntax.__getattr__(self, name)
        if result is not None:
            return result

        # Section からサブシンタックスを全て走査しても見つからなかった場合は
        # AttributeError を投げる
        raise AttributeError("'{}' object has no attribute '{}'".format(
            self.__class__.__name__, name))

class ProgramAssociationSection(Section):

    """Program Association Section PAT (ISO 13818-1 2.4.4.3)"""

    _pids = [0x00]
    _table_ids = [0x00]

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use = bslbf(1)
    reserved_1 = bslbf(2)
    section_length = uimsbf(12)
    transport_stream_id = uimsbf(16)
    reserved_2 = bslbf(2)
    version_number = uimsbf(5)
    current_next_indicator = bslbf(1)
    section_number = uimsbf(8)
    last_section_number = uimsbf(8)

    @loop(lambda self: self.section_length - 9)
    class pids(Syntax):
        program_number = uimsbf(16)
        reserved = bslbf(3)
        program_map_PID = uimsbf(13)

    CRC_32 = rpchof(32)

    @property
    def pmt_items(self):
        """program_number と program_map_PID のタプルを返すジェネレータ"""
        for pid in self.pids:
            if pid.program_number:
                yield (pid.program_number, pid.program_map_PID)

    @property
    def pmt_pids(self):
        """program_map_PID を返すジェネレータ"""
        for pid in self.pids:
            if pid.program_number:
                yield pid.program_map_PID

class ProgramMapSection(Section):

    """Program Map Section PMT (ISO 13818-1 2.4.4.8)"""

    _table_ids = [0x02]

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use = bslbf(1)
    reserved_1 = bslbf(2)
    section_length = uimsbf(12)
    program_number = uimsbf(16)
    reserved_2 = bslbf(2)
    version_number = uimsbf(5)
    current_next_indicator = bslbf(1)
    section_number = uimsbf(8)
    last_section_number = uimsbf(8)
    reserved_3 = bslbf(3)
    PCR_PID = uimsbf(13)
    reserved_4 = bslbf(4)
    program_info_length = uimsbf(12)
    descriptors = descriptors(program_info_length)

    @loop(lambda self: self.section_length - (13 + self.program_info_length))
    class maps(Syntax):
        stream_type = uimsbf(8)
        reserved_1 = bslbf(3)
        elementary_PID = uimsbf(13)
        reserved_2 = bslbf(4)
        ES_info_length = uimsbf(12)
        descriptors = descriptors(ES_info_length)

    CRC_32 = rpchof(32)

    @property
    def caption_pid(self):
        """字幕データのあるPIDを返す。

        字幕データはStream_typeが0x06(private data)で
        ストリーム識別記述子のcomponent_tagが0x87であるもの。
        参考: http://linux.papa.to/?date=20081224#p01

        """
        for stream in self.maps:
            try:
                if (stream.stream_type == 0x06 and
                    stream.descriptors[StreamIdentifierDescriptor
                        ][0].component_tag == 0x87):
                    return stream.elementary_PID
            except KeyError:
                pass

    def video_pids(self):
        "動画パケットの PID を返すジェネレータ"""

        video_types = (0x01, 0x02, 0x10)
        for stream in self.maps:
            if stream.stream_type in video_types:
                yield stream.elementary_PID

    def audio_pids(self):
        """音声パケットの PID を返すジェネレータ"""

        audio_types = (0x03, 0x04, 0x0F, 0x11)
        for stream in self.maps:
            if stream.stream_type in audio_types:
                yield stream.elementary_PID

class NetworkInformationSection(Section):

    """ネットワーク情報セクション NIT (ARIB-STD-B10-2-5.2.4)"""

    _pids = [0x10]
    _table_ids = [0x40, 0x41]

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use_1 = bslbf(1)
    reserved_1 = bslbf(2)
    section_length = uimsbf(12)
    network_id = uimsbf(16)
    reserved_2 = bslbf(2)
    version_number = uimsbf(5)
    current_next_indicator = bslbf(1)
    section_number = uimsbf(8)
    last_section_number = uimsbf(8)
    reserved_future_use_2 = bslbf(4)
    network_descriptors_length = uimsbf(12)
    network_descriptors = descriptors(network_descriptors_length)
    reserved_future_use_3 = bslbf(4)
    transport_stream_loop_length = uimsbf(12)

    @loop(transport_stream_loop_length)
    class transport_streams(Syntax):
        transport_stream_id = uimsbf(16)
        original_network_id = uimsbf(16)
        reserved_future_use = bslbf(4)
        transport_descriptors_length = uimsbf(12)
        descriptors = descriptors(transport_descriptors_length)

    CRC_32 = rpchof(32)

class ServiceDescriptionSection(Section):

    """サービス記述セクション SDT (ARIB-STD-B10-2-5.2.6)"""

    _pids = [0x11]
    _table_ids = [0x42, 0x46]

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use_1 = bslbf(1)
    reserved_1 = bslbf(2)
    section_length = uimsbf(12)
    transport_stream_id = uimsbf(16)
    reserved_2 = bslbf(2)
    version_number = uimsbf(5)
    current_next_indicator = bslbf(1)
    section_number = uimsbf(8)
    last_section_number = uimsbf(8)
    original_network_id = uimsbf(16)
    reserved_future_use_2 = bslbf(8)

    @loop(lambda self: self.section_length - 12)
    class services(Syntax):
        service_id = uimsbf(16)
        reserved_future_use = bslbf(3)
        EIT_user_defined_flags = bslbf(3)
        EIT_schedule_flag = bslbf(1)
        EIT_present_following_flag = bslbf(1)
        running_status = uimsbf(3)
        free_CA_mode = bslbf(1)
        descriptors_loop_length = uimsbf(12)
        descriptors = descriptors(descriptors_loop_length)

    CRC_32 = rpchof(32)

class BouquetAssociationSection(Section):

    """ブーケアソシエーションセクション BAT (ARIB-STD-B10-2-5.2.5)"""

    _pids = [0x11]
    _table_ids = [0x4A]

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use_1 = bslbf(1)
    reserved_1 = bslbf(2)
    section_length = uimsbf(12)
    bouquet_id = uimsbf(16)
    reserved_2 = bslbf(2)
    version_number = uimsbf(5)
    current_next_indicator = bslbf(1)
    section_number = uimsbf(8)
    last_section_number = uimsbf(8)
    reserved_future_use_2 = bslbf(4)
    bouquet_descriptors_length = uimsbf(12)
    bouquet_descriptors = descriptors(bouquet_descriptors_length)
    reserved_future_use_3 = bslbf(4)
    transport_stream_loop_length = uimsbf(12)

    @loop(transport_stream_loop_length)
    class transport_streams(Syntax):
        transport_stream_id = uimsbf(16)
        original_network_id = uimsbf(16)
        reserved_future_use = bslbf(4)
        transport_descriptors_length = uimsbf(12)
        descriptors = descriptors(transport_descriptors_length)

    CRC_32 = rpchof(32)

class EventInformationSection(Section):

    """イベント情報セクション EIT (ARIB-STD-B10-2-5.2.7)"""

    _pids = [0x12, 0x26, 0x27]
    _table_ids = range(0x4E, 0x70)

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use = bslbf(1)
    reserved_1 = bslbf(2)
    section_length = uimsbf(12)
    service_id = uimsbf(16)
    reserved_2 = bslbf(2)
    version_number = uimsbf(5)
    current_next_indicator = bslbf(1)
    section_number = uimsbf(8)
    last_section_number = uimsbf(8)
    transport_stream_id = uimsbf(16)
    original_network_id = uimsbf(16)
    segment_last_section_number = uimsbf(8)
    last_table_id = uimsbf(8)

    @loop(lambda self: self.section_length - 15)
    class events(Syntax):
        event_id = uimsbf(16)
        start_time = mjd(40)
        duration = bcd(24)
        running_status = uimsbf(3)
        free_CA_mode = bslbf(1)
        descriptors_loop_length = uimsbf(12)
        descriptors = descriptors(descriptors_loop_length)

    CRC_32 = rpchof(32)

class RunningStatusSection(Section):

    """進行状態セクション RST (ARIB-STD-B10-2-5.2.10)"""

    _pids = [0x13]
    _table_ids = [0x71]

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use = bslbf(1)
    reserved = bslbf(2)
    section_length = uimsbf(12)

    @loop(section_length)
    class statuses(Syntax):
        transport_stream_id = uimsbf(16)
        original_network_id = uimsbf(16)
        service_id = uimsbf(16)
        event_id = uimsbf(16)
        reserved_future_use = bslbf(5)
        running_status = uimsbf(3)

class TimeAndDateSection(Section):

    """時刻日付セクション TDT (ARIB-STD-B10-2-5.2.8)"""

    _pids = [0x14]
    _table_ids = [0x70]

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use = bslbf(1)
    reserved = bslbf(2)
    section_length = uimsbf(12)
    JST_time = mjd(40)

class TimeOffsetSection(Section):

    """時刻日付オフセットセクション TOT (ARIB-STD-B10-2-5.2.9)"""

    _pids = [0x14]
    _table_ids = [0x73]

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use = bslbf(1)
    resered1 = bslbf(2)
    section_length = uimsbf(12)
    JST_time = mjd(40)
    reserved_2 = bslbf(4)
    descriptors_loop_length = uimsbf(12)
    descriptors = descriptors(descriptors_loop_length)
    CRC_32 = rpchof(32)

class LocalEventInformationSection(Section):

    """ローカルイベント情報セクション LIT (ARIB-STD-B10-2-5.1.1)"""

    _pids = [0x20]
    _table_ids = [0xD0]

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use = bslbf(1)
    reserved_1 = bslbf(2)
    section_length = uimsbf(12)
    event_id = uimsbf(16)
    reserved_2 = bslbf(2)
    version_number = uimsbf(5)
    current_next_indicator = bslbf(1)
    section_number = uimsbf(8)
    last_section_number = uimsbf(8)
    service_id = uimsbf(16)
    transport_stream_id = uimsbf(16)
    original_network_id = uimsbf(16)

    @loop(lambda self: self.section_length - 15)
    class events(Syntax):
        local_event_id = uimsbf(16)
        reserved_fugure_use = bslbf(4)
        descriptors_loop_length = uimsbf(12)
        descriptors = descriptors(descriptors_loop_length)

    CRC_32 = rpchof(32)

class EventRelationSection(Section):

    """イベント関係セクション ERT (ARIB-STD-B10-2-5.1.2)"""

    _pids = [0x21]
    _table_ids = [0xD1]

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use_1 = bslbf(1)
    reserved_1 = bslbf(2)
    section_length = uimsbf(12)
    event_relation_id = uimsbf(16)
    reserved_2 = bslbf(2)
    version_number = uimsbf(5)
    current_next_indicator = bslbf(1)
    section_number = uimsbf(8)
    last_section_number = uimsbf(8)
    information_provider_id = uimsbf(16)
    relation_type = uimsbf(4)
    reserved_future_use_2 = bslbf(4)

    @loop(lambda self: self.section_length - 12)
    class references(Syntax):
        node_id = uimsbf(16)
        collection_mode = uimsbf(4)
        reserved_future_use_1 = bslbf(4)
        parent_node_id = uimsbf(16)
        referece_number = uimsbf(8)
        reserved_future_use_2 = bslbf(4)
        descriptors_loop_length = uimsbf(12)
        descriptors = descriptors(descriptors_loop_length)

    CRC_32 = rpchof(32)

class IndexTransmissionSection(Section):

    """番組インデックス送出情報セクション ITT (ARIB-STD-B10-2-5.1.3)"""

    _table_ids = [0xD2]

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use_1 = bslbf(1)
    reserved_1 = bslbf(2)
    section_length = uimsbf(12)
    event_id = uimsbf(16)
    reserved_2 = bslbf(2)
    version_number = uimsbf(5)
    current_next_indicator = bslbf(1)
    section_number = uimsbf(8)
    last_section_number = uimsbf(8)
    reserved_future_use_2 = uimsbf(4)
    descriptors_loop_length = uimsbf(12)
    descriptors = descriptors(descriptors_loop_length)
    CRC_32 = rpchof(32)

class PartialContentAnnouncementSection(Section):

    """差分配信告知セクション PCAT (ARIB-STD-B10-2-5.2.12)"""

    _pids = [0x22]
    _table_ids = [0xC2]

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use_1 = bslbf(1)
    reserved_1 = bslbf(2)
    section_length = uimsbf(12)
    event_relation_id = uimsbf(16)
    reserved_2 = bslbf(2)
    version_number = uimsbf(5)
    current_next_indicator = bslbf(1)
    section_number = uimsbf(8)
    last_section_number = uimsbf(8)
    information_provider_id = uimsbf(16)
    relation_type = uimsbf(4)
    reserved_future_use_2 = uimsbf(4)

    @loop(lambda self: self.section_length - 10)
    class relations(Syntax):
        node_id = uimsbf(16)
        collection_mode = uimsbf(4)
        reserved_future_use_1 = bslbf(4)
        parent_node_id = uimsbf(16)
        reference_number = uimsbf(8)
        reserved_future_use_2 = bslbf(4)
        descriptors_loop_length = uimsbf(12)
        descriptors = descriptors(descriptors_loop_length)

    CRC_32 = rpchof(32)

class StuffingSection(Section):

    """スタッフセクション ST (ARIB-STD-B10-2.5.2.11)"""

    _table_ids = [0x72]

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use = bslbf(1)
    reserved = bslbf(2)
    section_length = uimsbf(12)

    @loop(section_length)
    class data(Syntax):
        data_byte = uimsbf(8)

class BroadcasterInformationSection(Section):

    """ブロードキャスタ情報セクション BIT (ARIB-STD-B10-2-5.2.13)"""

    _pids = [0x24]
    _table_ids = [0xC4]

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use_1 = bslbf(1)
    reserved_1 = bslbf(2)
    section_length = uimsbf(12)
    original_network_id = uimsbf(16)
    reserved_2 = bslbf(2)
    version_number = uimsbf(5)
    current_next_indicator = bslbf(1)
    section_number = uimsbf(8)
    last_section_number = uimsbf(8)
    reserved_future_use_2 = bslbf(3)
    broadcast_view_propriety = bslbf(1)
    first_descriptors_length = uimsbf(12)
    descriptors = descriptors(first_descriptors_length)

    @loop(lambda self: self.section_length - (
            self.first_descriptors_length + 11))
    class broadcasters(Syntax):
        broadcaster_id = uimsbf(8)
        reserved_future_use = bslbf(4)
        broadcaster_descriptor_length = uimsbf(12)
        descriptors = descriptors(broadcaster_descriptor_length)

    CRC_32 = rpchof(32)

class NetworkBoardInformationSection(Section):

    """ネットワーク掲示板情報セクション NBIT (ARIB-STD-B10-2-5.14)

    FIXME: 未実装
    """

    _pids = [0x25]
    _table_ids = [0x40, 0x41]

class CommonDataSection(Section):

    """全受信機共通データセクション CDT (ARIB-STD-B21-12.2.2.2)"""

    _pids = [0x29]
    _table_ids = [0xC8]

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use_1 = bslbf(1)
    reserved_1 = bslbf(2)
    section_length = uimsbf(12)
    download_data_id = uimsbf(16)
    reserved_2 = bslbf(2)
    version_number = uimsbf(5)
    current_next_indicator = bslbf(1)
    section_number = uimsbf(8)
    last_section_number = uimsbf(8)
    original_network_id = uimsbf(16)
    data_type = uimsbf(8)
    reserved_future_use_2 = bslbf(4)
    descriptor_loop_length = uimsbf(12)
    descriptors = descriptors(descriptor_loop_length)

    @loop(lambda self: self.section_length - (
            self.descriptor_loop_length + 14))
    class data_modules(Syntax):
        data_module_byte = uimsbf(8)

    CRC_32 = rpchof(32)

class LinkedDescriptionSection(Section):

    """リンク記述セクション (ARIB-STD-B10-2-5.2.15)

    FIXME: 未実装
    """

    _table_ids = [0xC7]

class EntitlementControlMessage(Section):

    """ARIB-STD-B1, B21

    FIXME: 未実装
    """

    _table_ids = [0x82, 0x83]

class SoftwareDownloadTriggerSection(Section):

    """ARIB-STD-B1, B21

    FIXME: 未実装
    """

    _table_ids = [0xC3]

class CommonDataSection(Section):

    """ARIB-STD-B1, B21

    FIXME: 未実装
    """

    _pids = [0x29]

class DSMCCSection(Section):

    """ARIB-STD-B24-3-6.5

    FIXME: 未実装
    """

    _table_ids = [0x3A, 0x3B, 0x3C, 0x3D, 0x3E, 0x3F]

