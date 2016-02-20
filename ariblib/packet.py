import itertools


def packets(f, chunk_size=10000):
    """1パケットずつ返す"""

    packet_size = 188
    buffer_size = packet_size * chunk_size
    packets = iter(lambda: f.read(buffer_size), b'')
    indices = list(zip(
        range(0, buffer_size - packet_size + 1, packet_size),
        range(packet_size, buffer_size + 1, packet_size)))
    for packet in packets:
        for start, stop in indices:
            next_packet = packet[start:stop]
            if not next_packet:
                raise StopIteration
            yield next_packet


def transport_error_indicator(p):
    """パケットの transport_error_indicator を返す"""

    return (p[1] & 0x80) >> 7


def payload_unit_start_indicator(p):
    """パケットの payload_unit_start_indicator を返す"""

    return (p[1] & 0x40) >> 6


def transport_priority(p):
    """パケットの transport_priority を返す"""

    return (p[1] & 0x20) >> 5


def pid(p):
    """パケットの pid を返す"""

    return ((p[1] & 0x1F) << 8) | p[2]


def transport_scrambling_control(p):
    """パケットの transport_scrambling_control を返す"""

    return (p[3] & 0xC0) >> 6


def has_adaptation(p):
    """パケットが adaptation field を持っているかどうかを返す"""

    return (p[3] & 0x20) >> 5


def has_payload(p):
    """パケットが payload を持っているかどうかを返す"""

    return (p[3] & 0x10) >> 4


def continuity_counter(p):
    """パケットの continuity_counter を返す"""

    return p[3] & 0x0F


def adaptation_field(p):
    """パケットの adaptation_field を返す"""

    if not has_adaptation(p):
        return b''

    start = 4
    adaptation_length = p[start]
    end = start + adaptation_length + 1
    return p[start:end]


def payload(p):
    """パケットの payload を返す"""

    if not has_payload(p):
        return bytearray(), bytearray()

    start = 4
    if has_adaptation(p):
        adaptation_length = p[start]
        start += 1 + adaptation_length
    if not payload_unit_start_indicator(p):
        return bytearray(), bytearray(p[start:])
    pointer = p[start]
    prev_start = start + 1
    start += 1 + pointer
    return bytearray(p[prev_start:start]), bytearray(p[start:])


def payloads(ts):
    """payload を pid ごとに返す"""

    pids = {}
    for packet in ts:
        this_pid = pid(packet)
        prev_packet, next_packet = payload(packet)
        if payload_unit_start_indicator(packet):
            if this_pid in pids:
                pids[this_pid].extend(prev_packet)
                table_id = pids[this_pid][0]
                yield this_pid, table_id, bytes(pids[this_pid])
            pids[this_pid] = next_packet
        elif this_pid in pids:
            pids[this_pid].extend(next_packet)
