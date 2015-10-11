from io import BufferedReader, BytesIO, FileIO


class TransportStreamFile(BufferedReader):

    PACKET_SIZE = 188

    def __init__(self, path, chunk_size=10000):
        io = BytesIO if isinstance(path, bytearray) else FileIO
        BufferedReader.__init__(self, io(path))
        self.chunk_size = chunk_size

    def __iter__(self):
        packet_size = self.PACKET_SIZE
        chunk_size = self.chunk_size
        buffer_size = packet_size * chunk_size
        packets = iter(lambda: self.read(buffer_size), b'')
        for packet in packets:
            for start, stop in zip(
                    range(0, buffer_size - packet_size + 1, packet_size),
                    range(packet_size, buffer_size + 1, packet_size)):
                next_packet = packet[start:stop]
                if not next_packet:
                    raise StopIteration
                yield next_packet

    def __next__(self):
        return self.read(self.PACKET_SIZE)

    def sections(self, Section):
        for packet in self:
            if pid(packet) not in Section.__pids__:
                continue
            prev, current = payload(packet)
            yield Section(current)


def tsopen(path, chunk_size=10000):
    return TransportStreamFile(path, chunk_size)


def transport_error_indicator(packet):
    return (packet[1] & 0x80) >> 7


def payload_unit_start_indicator(packet):
    return (packet[1] & 0x40) >> 6


def transport_priority(packet):
    return (packet[1] & 0x20) >> 5


def pid(packet):
    return ((packet[1] & 0x1F) << 8) | packet[2]


def transport_scrambling_control(packet):
    return (packet[3] & 0xC0) >> 6


def has_adaptation(packet):
    return (packet[3] & 0x20) >> 5


def has_payload(packet):
    return (packet[3] & 0x10) >> 4


def continuity_counter(packet):
    return packet[3] & 0x0F


def payload(packet):
    if not has_payload(packet):
        return b'', b''

    start = 4

    if has_adaptation(packet):
        adaptation_length = packet[start]
        start += 1 + adaptation_length

    if not payload_unit_start_indicator(packet):
        return b'', packet[start:]

    packet_start_code_prefix_end = start + 3
    packet_start_code_prefix = packet[start:packet_start_code_prefix_end]
    if packet_start_code_prefix == b'\x00\x00\x01':
        return b'', packet[start:]

    pointer = packet[start]
    prev_start = start + 1
    start += 1 + pointer
    return packet[prev_start:start], packet[start:]
