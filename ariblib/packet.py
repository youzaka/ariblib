from io import BufferedReader, FileIO


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


def tsopen(path, chunk_size=10000):
    return TransportStreamFile(path, chunk_size)
