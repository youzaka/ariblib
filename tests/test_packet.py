from io import BytesIO
from unittest import TestCase

from ariblib import packet, tsopen


class TestPacket(TestCase):

    def setUp(self):
        packet = bytearray(
            b'G`\x00\x19\x00\x00\xb0\x1d\x7f\xe3\xe7\x00\x00\x00\x00\xe0\x10'
            b'\x04\x18\xe1\x01\x04\x19\xe1\x02\x05\x98\xff\xc8\x04\x9f\xe7\xf0'
            b'\xaf\xd5A\xae\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
            b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
            b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
            b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
            b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
            b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
            b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
            b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
            b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
            b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff')
        with tsopen(packet) as ts:
            self.packet = next(ts)

    def test_transport_error_indicator(self):
        self.assertFalse(packet.transport_error_indicator(self.packet))

    def test_payload_unit_start_indicator(self):
        self.assertTrue(packet.payload_unit_start_indicator(self.packet))

    def test_transort_priority(self):
        self.assertEqual(packet.transport_priority(self.packet), 1)

    def test_pid(self):
        self.assertEqual(packet.pid(self.packet), 0)

    def test_transport_scrambling_control(self):
        self.assertFalse(packet.transport_scrambling_control(self.packet))

    def test_has_adaptation(self):
        self.assertFalse(packet.has_adaptation(self.packet))

    def test_has_payload(self):
        self.assertTrue(packet.has_payload(self.packet))

    def test_continuity_conter(self):
        self.assertEqual(packet.continuity_counter(self.packet),  9)
