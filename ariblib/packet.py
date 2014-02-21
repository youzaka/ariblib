#!/usr/bin/env python3.2

from collections import defaultdict
from datetime import timedelta
from io import BufferedReader, FileIO
from itertools import chain

from ariblib.mnemonics import (
    bcdtime,
    bslbf,
    case,
    char,
    loop,
    otm,
    raw,
    times,
    uimsbf,
)
from ariblib.syntax import Syntax
from ariblib.sections import Section

"""
パケット層の定義

188バイトずつの各パケットを class として実装するとかなり遅くなるので、
パケットについては bytearray のまま受け渡して、関数で適宜対応することにした。
"""


class TransportStreamFile(BufferedReader):

    """TSファイル"""

    PACKET_SIZE = 188

    def __init__(self, path, chunk_size=10000):
        BufferedReader.__init__(self, FileIO(path))
        self.chunk_size = chunk_size
        self._callbacks = dict()

    def __iter__(self):
        packet_size = self.PACKET_SIZE
        chunk_size = self.chunk_size
        buffer_size = packet_size * chunk_size
        packets = iter(lambda: self.read(buffer_size), b'')
        for packet in packets:
            for start, stop in zip(
                range(0, buffer_size - packet_size + 1, packet_size),
                range(packet_size, buffer_size + 1, packet_size)
            ):
                next = packet[start:stop]
                if not next:
                    raise StopIteration
                yield next

    def __next__(self):
        return self.read(self.PACKET_SIZE)

    def on(self, Section):
        """セクションごとにコールバック関数を設定する
        いまのところ、一つのセクションについてコールバック関数は1つのみ定義できる。
        """

        def attach_callback(callback):
            self._callbacks[Section] = callback
        return attach_callback

    def execute(self):
        """指定されたセクションがyieldされるごとにコールバック関数を実行する"""

        for section in self.sections(*self._callbacks.keys()):
            self._callbacks[type(section)](section)

    def sections(self, *Sections):
        """パケットストリームから指定のセクションを返す"""

        buf = defaultdict(bytearray)

        target_pids =\
            set(chain.from_iterable(Section._pids for Section in Sections))
        table_map = defaultdict(set)
        target_ids = dict()
        for Section in Sections:
            for PID in Section._pids:
                for table_id in Section._table_ids:
                    target_ids[(PID, table_id)] = Section
                    table_map[PID].add(table_id)

        for packet in self:
            PID = pid(packet)
            if PID not in target_pids:
                continue

            buffer = buf[PID]
            table_ids = table_map[PID]
            prev, current = payload(packet)
            if payload_unit_start_indicator(packet):
                if buffer:
                    buffer.extend(prev)
                while buffer and buffer[0] != 0xFF:
                    if buffer[0] in table_ids:
                        section = target_ids[(PID, buffer[0])](buffer[:])
                        yield section
                    try:
                        if buffer[0:3] == b'\x00\x00\x01':
                            break
                        else:
                            next_start =\
                                ((buffer[1] & 0x0F) << 8 | buffer[2]) + 3
                            buffer[:] = buffer[next_start:]
                    except (IndexError, AttributeError):
                        break
                buffer[:] = current
            elif not buffer:
                continue
            else:
                buffer.extend(current)

        # 残ったバッファを片付ける
        for PID, buffer in buf.items():
            if buffer and buffer[0] in table_ids:
                section = target_ids[(PID, buffer[0])](buffer[:])
                if section.isfull():
                    yield section

    tables = sections

    def get_caption_pid(self):
        """字幕パケットの PID を返す

        FIXME: 2か国語対応の場合複数の PID で字幕が提供されているかも? (未確認)
        """

        from ariblib.sections import (
            ProgramAssociationSection,
            ProgramMapSection,
        )
        from ariblib.descriptors import StreamIdentifierDescriptor

        pat = next(self.sections(ProgramAssociationSection))
        ProgramMapSection._pids = list(pat.pmt_pids)
        for pmt in self.sections(ProgramMapSection):
            for tsmap in pmt.maps:
                if tsmap.stream_type != 0x06:
                    continue
                for si in tsmap.descriptors.get(StreamIdentifierDescriptor,
                                                []):
                    if si.component_tag == 0x87:
                        return tsmap.elementary_PID

    def get_video_pid(self, video_encode_format):
        """指定のエンコードフォーマットの動画PIDを返す"""

        from ariblib.sections import (
            ProgramAssociationSection,
            ProgramMapSection,
        )
        from ariblib.descriptors import VideoDecodeControlDescriptor

        pat = next(self.sections(ProgramAssociationSection))
        ProgramMapSection._pids = list(pat.pmt_pids)
        for pmt in self.sections(ProgramMapSection):
            for tsmap in pmt.maps:
                for vdc in tsmap.descriptors.get(VideoDecodeControlDescriptor,
                                                 []):
                    if vdc.video_encode_format == video_encode_format:
                        return tsmap.elementary_PID

    def pcrs(self):
        """adaptation filed にある PCR から求めた timedelta オブジェクトを返す

        FIXME: PCR フラグでなく OPCR フラグが立っているときに、この関数は OPCR を返す
        """

        for packet in self:
            if has_adaptation(packet) and packet[4] and packet[5]:
                pcr = ((packet[6] << 25) | (packet[7] << 17) |
                       (packet[8] << 9) | (packet[9] << 1) |
                       ((packet[10] & 0x80) >> 7))
                yield timedelta(seconds=pcr / 90000)


def tsopen(path, chunk=10000):
    """TransportStreamFileオブジェクトを返すラッパー関数"""
    return TransportStreamFile(path, chunk)


def transport_error_indicator(packet):
    """パケットの transport_error_indocator を返す"""
    return (packet[1] & 0x80) >> 7


def payload_unit_start_indicator(packet):
    """パケットの payload_unit_start_indicator を返す"""
    return (packet[1] & 0x40) >> 6


def transport_priority(pakcet):
    """パケットの transport_priority を返す"""
    return (packet[1] & 0x20) >> 5


def pid(packet):
    """パケットの pid を返す"""
    return ((packet[1] & 0x1F) << 8) | packet[2]


def transport_scrambling_control(packet):
    return (packet[3] & 0xC0) >> 6


def has_adaptation(packet):
    """このパケットが adaptation field を持っているかどうかを返す"""
    return (packet[3] & 0x20) >> 5


def has_payload(packet):
    """このパケットが payload を持っているかどうかを返す"""
    return (packet[3] & 0x10) >> 4


def continuity_counter(packet):
    """このパケットの continuity_counter を返す"""
    return packet[3] & 0x0F


def adaptation_field(packet):
    """パケットから adaptaton field 部分を返す"""

    if not has_adaptation(packet):
        return b''

    start = 4
    adaptation_length = packet[start]
    end = start + adaptation_length + 1
    return AdaptationField(packet[start:end])


def payload(packet):
    """パケットから payload 部分を返す

    args:
    packet - payloadを求めたい TS パケット

    return:
    (前のパケットの payload の続き, このパケットの payload) の tuple
    """

    if not has_payload(packet):
        return (b'', b'')

    start = 4

    if has_adaptation(packet):
        adaptation_length = packet[start]
        start += 1 + adaptation_length

    if not payload_unit_start_indicator(packet):
        return (b'', packet[start:])

    packet_start_code_prefix = packet[start:start + 3]
    if packet_start_code_prefix == b'\x00\x00\x01':
        return (b'', packet[start:])

    pointer = packet[start]
    prev_start = start + 1
    start += 1 + pointer
    return (packet[prev_start:start], packet[start:])


class AdaptationField(Syntax):

    """ISO/IEC 13818-1 2.4.3.5"""

    adaptation_field_length = uimsbf(8)
    discontinuity_indicator = bslbf(1)
    random_access_indicator = bslbf(1)
    elementary_stream_priority_indicator = bslbf(1)
    PCR_flag = bslbf(1)
    OPCR_flag = bslbf(1)
    splicing_point_flag = bslbf(1)
    transport_private_data_flag = bslbf(1)
    adaptation_field_extension_flag = bslbf(1)

    @case(PCR_flag)
    class with_PCR(Syntax):
        program_clock_reference_base = uimsbf(33)
        reserved_1 = bslbf(6)
        program_clock_reference_extension = uimsbf(9)

    @case(OPCR_flag)
    class with_OPCR(Syntax):
        original_program_clock_reference_base = uimsbf(33)
        reserved_2 = bslbf(6)
        original_program_clock_reference_extension = uimsbf(9)

    @case(splicing_point_flag)
    class with_splicing(Syntax):
        splice_countdown = uimsbf(8)  # tcimsbf

    @case(transport_private_data_flag)
    class with_transport_private_data(Syntax):
        transport_private_data_length = uimsbf(8)
        private_data_byte = bslbf(transport_private_data_length)


class SynchronizedPacketizedElementaryStream(Section):

    """ISO/IEC 13818-1 2.4.3.7

    FIXME: 字幕 PES パケット専用の実装になっている
    字幕部分の仕様は ARIB STD-B24-1-3-9
    """

    packet_start_code_prefix = bslbf(24)
    stream_id = uimsbf(8)
    PES_packet_length = uimsbf(16)
    should_be_10 = bslbf(2)
    PES_scrambling_control = bslbf(2)
    PES_priority = bslbf(1)
    data_alignment_indicator = bslbf(1)
    copyright = bslbf(1)
    original_or_copy = bslbf(1)
    PTS_DTS_flags = bslbf(2)
    ESCR_flag = bslbf(1)
    ES_rate_flag = bslbf(1)
    DSM_trick_mode_flag = bslbf(1)
    additional_copy_into_flag = bslbf(1)
    PES_CRC_flag = bslbf(1)
    PES_extension_flag = bslbf(1)
    PES_header_data_length = uimsbf(8)
    should_be_0010 = bslbf(4)
    PTS_1 = uimsbf(3)
    marker_bit_1 = bslbf(1)
    PTS_2 = uimsbf(15)
    marler_bit_2 = bslbf(1)
    PTS_3 = uimsbf(15)
    marker_bit_3 = bslbf(1)
    PES_private_data_flag = bslbf(1)
    pack_header_field_flag = bslbf(1)
    program_packet_sequence_counter_flag = bslbf(1)
    P_STD_buffer_flag = bslbf(1)
    reserved4 = bslbf(3)
    PES_extension_flag_2 = bslbf(1)
    PES_private_data = bslbf(128)
    stuffing_byte = bslbf(lambda self: self.PES_header_data_length - 22)
    data_identifier = uimsbf(8)
    private_stream_id = uimsbf(8)
    reserved_future_use = bslbf(4)
    PES_data_packet_header_length = uimsbf(4)
    PES_data_private_data_byte = bslbf(PES_data_packet_header_length)
    data_group_id = uimsbf(6)
    data_group_version = bslbf(2)
    data_group_link_number = uimsbf(8)
    last_data_group_link_number = uimsbf(8)
    data_group_size = uimsbf(16)

    @case(lambda self: self.data_group_id in (0x0, 0x20))
    class with_languages(Syntax):
        """ARIB-STD-B24-1-3-9.3.1 表9-3 字幕管理データ"""

        TMD = bslbf(2)
        reserved10 = bslbf(6)

        @case(lambda self: self.TMD == 0b10)
        class with_OTM(Syntax):
            OTM = otm(40)

        num_languages = uimsbf(8)

        @times(num_languages)
        class languages(Syntax):
            language_tag = bslbf(3)
            reserved11 = bslbf(1)
            DMF1 = bslbf(2)
            DMF2 = bslbf(2)

            @case(lambda self: self.DMF1 == 0b11)
            class with_DC(Syntax):
                DC = bslbf(8)

            ISO_639_language_code = char(24)
            format = bslbf(4)
            TCS = bslbf(2)
            rollup_mode = bslbf(2)

    @case(lambda self: self.data_group_id not in (0x0, 0x20))
    class without_languages(Syntax):
        """ARIB-STD-B24-1-3-9.3.2 表9-10 字幕文データ"""

        TMD = bslbf(2)
        reserved10 = bslbf(6)

        @case(lambda self: self.TMD in (0b01, 0b10))
        class with_STM(Syntax):
            STM = bcdtime(40)

    data_unit_loop_length = uimsbf(24)

    @loop(data_unit_loop_length)
    class data_units(Syntax):
        unit_separator = uimsbf(8)
        data_unit_parameter = uimsbf(8)

        @case(lambda self: self.data_unit_parameter == 0x20)
        class CProfileString(Syntax):
            data_unit_size = uimsbf(24)
            data_unit_data = raw(data_unit_size)

        @case(lambda self: self.data_unit_parameter == 0x30)
        class DRCSString(Syntax):
            """ARIB-STD-B24-1-2-D 表D-1 DRCS_data_structure

            FIXME: width が16固定"""

            data_unit_size = uimsbf(24)
            number_of_code = uimsbf(8)

            @times(number_of_code)
            class codes(Syntax):
                character_code = uimsbf(16)
                number_of_font = uimsbf(8)

                @times(number_of_font)
                class fonts(Syntax):
                    font_id = uimsbf(4)
                    mode = bslbf(4)
                    depth = uimsbf(8)
                    width = uimsbf(8)
                    height = uimsbf(8)

                    @times(height)
                    class patterns(Syntax):
                        pattern_data = raw(16)

    @property
    def pts(self):
        pts = (self.PTS_1 << 30) | (self.PTS_2 << 15) | self.PTS_3
        pts_hz = 90000
        second = pts / pts_hz
        return timedelta(seconds=second)

    def isfull(self):
        """section_length などで指定された分以上の
        パケットを持っているかどうかを返す"""

        return self.PES_packet_length <= len(self) + 3


def raw_dump(packet):
    return ' '.join(map(lambda s: format(s, '02X'), packet))
