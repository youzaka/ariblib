from unittest import TestCase

from ariblib import adaptation, packet


class TestAdaptation(TestCase):

    def test_adaptation_field_length(self):
        p = b'\xB7\x10\xD2\x2D\x74\x82\x80\xF9'
        expected = 183
        self.assertTrue(adaptation.adaptation_field_length(p), expected)

    def test_discontinuity_indicator(self):
        p = b'\xB7\x10\xD2\x2D\x74\x82\x80\xF9'
        self.assertFalse(adaptation.discontinuity_indicator(p))

    def test_random_access_indicator(self):
        p = b'\xB7\x10\xD2\x2D\x74\x82\x80\xF9'
        self.assertFalse(adaptation.random_access_indicator(p))

    def test_elementary_stream_priority_indicator(self):
        p = b'\xB7\x10\xD2\x2D\x74\x82\x80\xF9'
        self.assertFalse(adaptation.elementary_stream_priority_indicator(p))

    def test_pcr_flag(self):
        p = b'\xB7\x10\xD2\x2D\x74\x82\x80\xF9'
        self.assertTrue(adaptation.pcr_flag(p))

    def test_opcr_flag(self):
        p = b'\xB7\x10\xD2\x2D\x74\x82\x80\xF9'
        self.assertFalse(adaptation.opcr_flag(p))

    def test_splicing_point_flag(self):
        p = b'\xB7\x10\xD2\x2D\x74\x82\x80\xF9'
        self.assertFalse(adaptation.splicing_point_flag(p))

    def test_transport_private_data_flag(self):
        p = b'\xB7\x10\xD2\x2D\x74\x82\x80\xF9'
        self.assertFalse(adaptation.transport_private_data_flag(p))

    def test_adaptation_field_extension_flag(self):
        p = b'\xB7\x10\xD2\x2D\x74\x82\x80\xF9'
        self.assertFalse(adaptation.adaptation_field_extension_flag(p))
