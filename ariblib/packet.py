#!/usr/bin/env python3.2

from collections import defaultdict
from io import BufferedReader, FileIO

from ariblib import pat, pmt

"""
パケット層の定義

188バイトずつの各パケットを class として実装するとかなり遅くなるので、
bytearray のまま受け渡して、関数で適宜対応することにした。
"""

class TransportStreamFile(BufferedReader):

    PACKET_SIZE = 188

    def __init__(self, path, chunk_size=10000):
        BufferedReader.__init__(self, FileIO(path))
        self.chunk_size = chunk_size
    def __iter__(self):
        packet_size = self.PACKET_SIZE
        chunk_size = self.chunk_size
        buffer_size = packet_size * chunk_size
        packets = iter(lambda: self.read(buffer_size), b'')
        return (packet[start:stop] for packet in packets
            for start, stop in zip(range(0, buffer_size - packet_size, packet_size),
                                   range(packet_size, buffer_size, packet_size)))
    def __next__(self):
        return self.read(self.PACKET_SIZE)

    def tables(self, pids, table_ids=None):
        """パケットストリームから指定の tid, table_id のテーブルを返す

        args:
        pids - 取得したい PID のリスト
        table_ids - 取得したい table_id のリスト。指定のない場合は table_id で絞込みしない

        return:
        テーブルを構成するバイト列
        """

        buf = defaultdict(bytearray)
        try:
            for packet in self:
                PID = pid(packet)
                if PID not in pids:
                    continue

                buffer = buf[PID]
                prev, current = payload(packet)
                if payload_unit_start_indicator(packet):
                    if (buffer and (not table_ids or buffer[0] in table_ids)):
                        buffer.extend(prev)
                        yield buffer[:]
                    buffer[:] = current
                elif not buffer:
                    continue
                else:
                    buffer.extend(current)
        except IndexError:
            raise StopIteration

    def video_pids(self):
        video_types = (0x01, 0x02, 0x10)
        pmt.pids = list(pat.pmt_pids())
        table = next(pmt.tables())
        for section in pmt.sections(table):
            if pmt.stream_type(section) in video_types:
                yield pmt.elementary_pid(section)

    def audio_pids(self):
        audio_types = (0x03, 0x04, 0x0F, 0x11)
        pmt.pids = list(pat.pmt_pids())
        table = next(pmt.tables())
        for section in pmt.sections(table):
            if pmt.stream_type(section) in video_types:
                yield pmt.elementary_pid(section)

    def get_caption_pid(self):
        pmt.pids = next(pat.pmt_pids(self))
        for table in pmt.tables(self):
            for section in pmt.sections(table):
                if pmt.stream_type(section) == 0x06:
                    for descriptor in pmt.descriptors(section):
                        if descriptor[0] == 0x52 and descriptor[2] == 0x87:
                            return pmt.elementary_pid(section)

def pcrs(ts):
    """adaptation filed にある PCR から求めた timedelta オブジェクトを返す

    FIXME: PCR フラグでなく OPCR フラグが立っているときに、この関数は OPCR を返す
    """

    for packet in self:
        if has_adaptation(packet) and packet[4] and packet[5]:
            pcr = ((packet[6] << 25) | (packet[7] << 17) |
                   (packet[8] << 9) | (packet[9] << 1) |
                   ((packet[10] & 0x80) >> 7))
            yield timedelta(seconds=pcr/90000)

def payload_unit_start_indicator(packet):
    """パケットの payload_unit_start_indicator を返す"""
    return (packet[1] & 0x40) >> 5

def pid(packet):
    """パケットの pid を返す"""
    return ((packet[1] & 0x1F) << 8) | packet[2]

def has_adaptation(packet):
    """このパケットが adaptation field を持っているかどうかを返す"""
    return (packet[3] & 0x20) >> 5

def has_payload(packet):
    """このパケットが payload を持っているかどうかを返す"""
    return (packet[3] & 0x10) >> 4

def adaptation_field(packet):
    """パケットから adaptaton field 部分を返す"""

    if not has_adaptation(packet):
        return b''

    start = 4
    adaptation_length = packet[start]
    end = start + adaptation_length + 1
    return packet[start:end]

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

    packet_start_code_prefix = packet[start:start+3]
    if packet_start_code_prefix == b'\x00\x00\x01':
        return (b'', packet[start:])

    pointer = packet[start]
    prev_start = start + 1
    start += 1 + pointer
    return (packet[prev_start:start], packet[start:])

