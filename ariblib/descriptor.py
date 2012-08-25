#!/usr/bin/env python3.2


def descriptors(packet):
    index = 0
    length = len(packet)
    while index < length:
        descriptor_length = packet[index+1]
        descriptor_last = descriptor_length + 2
        yield packet[index:index+descriptor_last]
        index += descriptor_last


