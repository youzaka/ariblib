from unittest import TestCase

from ariblib import packet


class TestPacket(TestCase):

    def test_transport_error_indicator(self):
        p = b'\x47\x40\x12\x18'
        self.assertFalse(packet.transport_error_indicator(p))

    def test_payload_unit_start_indicator(self):
        p = b'\x47\x40\x12\x18'
        self.assertTrue(packet.payload_unit_start_indicator(p))

    def test_transport_priority(self):
        p = b'\x47\x40\x12\x18'
        self.assertFalse(packet.transport_priority(p))

    def test_pid(self):
        p = b'\x47\x40\x12\x18'
        expected = 0x12
        self.assertTrue(packet.pid(p), expected)

    def test_transort_scrambling_control(self):
        p = b'\x47\x40\x12\x18'
        self.assertFalse(packet.transport_scrambling_control(p))

    def test_has_adaptation(self):
        p = b'\x47\x40\x12\x18'
        self.assertFalse(packet.has_adaptation(p))

    def test_has_payload(self):
        p = b'\x47\x40\x12\x18'
        self.assertTrue(packet.has_payload(p))

    def test_continuity_counter(self):
        p = b'\x47\x40\x12\x18'
        expected = 8
        self.assertEqual(packet.continuity_counter(p), expected)
