from io import BytesIO
from unittest import TestCase

from ariblib import tsopen
from ariblib.binary import unhexlify
from ariblib.sections import NetworkInformationSection


class TestNetworkInformationSection(TestCase):

    def test_nit(self):
        packet = '''
            47 60 10 1D 00 40 F0 73 7E 87 C7 00 00 F0 0D 40
            07 45 6C 35 7E 1B 7E B7 FE 02 03 01 F0 59 7E 87
            7E 87 F0 53 41 12 5C 38 01 5C 39 01 5C 3A 01 5C
            3F A1 5D B8 C0 5D B9 C0 FA 18 AA CA 0E 16 0F BA
            11 88 0D 98 10 62 0F 90 10 38 11 5E 0D 1A 0D 6E
            13 02 FB 04 5D B8 5D B9 CD 1D 09 2E 1B 7E D4 CF
            CB D9 CF 21 21 CD D8 0F 04 5C 38 5C 39 5C 3A 5C
            3F AF 02 5D B8 5D B9 FC 74 55 62 FF FF FF FF FF
            FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
            FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
            FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
            FF FF FF FF FF FF FF FF FF FF FF FF
        '''

        with tsopen(unhexlify(packet)) as ts:
            nit = next(ts.sections(NetworkInformationSection))
            self.assertEqual(nit.table_id, 0x40)
            self.assertTrue(nit.section_syntax_indicator)
            self.assertEqual(nit.section_length, 115)
            self.assertEqual(nit.network_id, 0x7E87)
            self.assertEqual(nit.version_number, 0x03)
            self.assertTrue(nit.current_next_indicator)
            self.assertEqual(nit.section_number, 0)
            self.assertEqual(nit.last_section_number, 0)

            network_descriptors = nit.network_descriptors
            desc1 = next(network_descriptors)
            self.assertEqual(desc1.descriptor_tag, 0x40)
            self.assertEqual(str(desc1.char), '東京7')

            desc2 = next(network_descriptors)
            self.assertEqual(desc2.descriptor_tag, 0xFE)
            self.assertEqual(desc2.broadcasting_flag, 0)
            self.assertEqual(desc2.broadcasting_identifier, 0x03)
            self.assertEqual(desc2.additional_broadcasting_identification,
                             0x01)
            with self.assertRaises(StopIteration):
                next(network_descriptors)

            streams = nit.transport_streams
            stream1 = next(streams)
            self.assertEqual(stream1.transport_stream_id, 0x7E87)
            self.assertEqual(stream1.original_network_id, 0x7E87)
            stream1_descriptors = stream1.descriptors
            stream1_desc1 = next(stream1_descriptors)
            self.assertEqual(stream1_desc1.descriptor_tag, 0x41)
            stream1_desc1_services = stream1_desc1.services
            stream1_desc1_service1 = next(stream1_desc1_services)
            self.assertEqual(stream1_desc1_service1.service_id, 0x5C38)
            self.assertEqual(stream1_desc1_service1.service_type, 0x01)
            stream1_desc1_service2 = next(stream1_desc1_services)
            self.assertEqual(stream1_desc1_service2.service_id, 0x5C39)
            self.assertEqual(stream1_desc1_service2.service_type, 0x01)
            stream1_desc1_service3 = next(stream1_desc1_services)
            self.assertEqual(stream1_desc1_service3.service_id, 0x5C3A)
            self.assertEqual(stream1_desc1_service3.service_type, 0x01)
            stream1_desc1_service4 = next(stream1_desc1_services)
            self.assertEqual(stream1_desc1_service4.service_id, 0x5C3F)
            self.assertEqual(stream1_desc1_service4.service_type, 0xA1)
            stream1_desc1_service5 = next(stream1_desc1_services)
            self.assertEqual(stream1_desc1_service5.service_id, 0x5DB8)
            self.assertEqual(stream1_desc1_service5.service_type, 0xC0)
            stream1_desc1_service6 = next(stream1_desc1_services)
            self.assertEqual(stream1_desc1_service6.service_id, 0x5DB9)
            self.assertEqual(stream1_desc1_service6.service_type, 0xC0)
            with self.assertRaises(StopIteration):
                next(stream1_desc1_services)
            stream1_desc2 = next(stream1_descriptors)
            self.assertEqual(stream1_desc2.descriptor_tag, 0xFA)
            self.assertEqual(stream1_desc2.area_code, 0xAAC)
            self.assertEqual(stream1_desc2.guard_interval, 2)
            self.assertEqual(stream1_desc2.transmission_mode, 2)
            stream1_desc2_freqs = stream1_desc2.freqs
            self.assertEqual(next(stream1_desc2_freqs).frequency, 0x0E16)
            self.assertEqual(next(stream1_desc2_freqs).frequency, 0x0FBA)
            self.assertEqual(next(stream1_desc2_freqs).frequency, 0x1188)
            self.assertEqual(next(stream1_desc2_freqs).frequency, 0x0D98)
            self.assertEqual(next(stream1_desc2_freqs).frequency, 0x1062)
            self.assertEqual(next(stream1_desc2_freqs).frequency, 0x0F90)
            self.assertEqual(next(stream1_desc2_freqs).frequency, 0x1038)
            self.assertEqual(next(stream1_desc2_freqs).frequency, 0x115E)
            self.assertEqual(next(stream1_desc2_freqs).frequency, 0x0D1A)
            self.assertEqual(next(stream1_desc2_freqs).frequency, 0x0D6E)
            self.assertEqual(next(stream1_desc2_freqs).frequency, 0x1302)
            with self.assertRaises(StopIteration):
                next(stream1_desc2_freqs)
            stream1_desc3 = next(stream1_descriptors)
            self.assertEqual(stream1_desc3.descriptor_tag, 0xFB)
            stream1_desc3_services = stream1_desc3.services
            stream1_desc3_service1 = next(stream1_desc3_services)
            self.assertEqual(stream1_desc3_service1.service_id, 0x5DB8)
            stream1_desc3_service2 = next(stream1_desc3_services)
            self.assertEqual(stream1_desc3_service2.service_id, 0x5DB9)
