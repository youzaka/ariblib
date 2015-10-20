from io import BytesIO
from unittest import TestCase

from ariblib import tsopen
from ariblib.binary import unhexlify
from ariblib.sections import ServiceDescriptionSection


class TestServiceDescriptionSection(TestCase):

    def test_sdt(self):
        packet = '''
            47 60 11 11 00 42 F0 DB 7E 87 C5 00 00 7E 87 FF
            5C 38 F3 00 1D 48 0F 01 00 0C 1B 7E D4 CF CB D9
            CF 21 21 CD D8 B1 CF 07 01 FE 10 F0 06 00 01 C1
            01 84 5C 39 F3 00 19 48 0F 01 00 0C 1B 7E D4 CF
            CB D9 CF 21 21 CD D8 B1 CF 03 02 FE 10 C1 01 84
            5C 3A F3 00 1D 48 0F 01 00 0C 1B 7E D4 CF CB D9
            CF 21 21 CD D8 B2 CF 07 01 FE 11 F0 06 00 02 C1
            01 84 5C 3F F1 00 20 48 12 A1 00 0F 1B 7E D4 CF
            CB D9 CF 21 21 CD D8 4E 57 3B 7E CF 07 01 FE 10
            F0 06 00 01 C1 01 84 5D B8 E5 00 1F 48 10 C0 00
            0D 1B 7E CD D8 1B 7C EF F3 BB B0 1B 7E B1 CF 08
            03 89 1B 7E CD D8 D4 D6 C1 01 88 5D
            47 20 11 12 B9 E5 00 1F 48 10 C0 00 0D 1B 7E CD
            D8 1B 7C EF F3 BB B0 1B 7E B2 CF 08 03 89 1B 7E
            CD D8 D4 D6 C1 01 88 2D 82 29 2B FF FF FF FF FF
            FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
            FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
            FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
            FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
            FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
            FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
            FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
            FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
            FF FF FF FF FF FF FF FF FF FF FF FF
        '''

        with tsopen(unhexlify(packet)) as ts:
            sdt = next(ts.sections(ServiceDescriptionSection))
            self.assertEqual(sdt.table_id, 0x42)
            self.assertTrue(sdt.section_syntax_indicator)
            self.assertEqual(sdt.transport_stream_id, 0x7E87)
            self.assertEqual(sdt.version_number, 2)
            self.assertTrue(sdt.current_next_indicator)
            self.assertEqual(sdt.section_number, 0)
            self.assertEqual(sdt.last_section_number, 0)
            self.assertEqual(sdt.original_network_id, 0x7E87)

            services = sdt.services
            service1 = next(services)
            self.assertEqual(service1.service_id, 0x5C38)
            self.assertEqual(service1.EIT_user_defined_flags, 4)
            self.assertTrue(service1.EIT_schedule_flag)
            self.assertTrue(service1.EIT_present_following_flag)
            self.assertEqual(service1.running_status, 0)
            self.assertEqual(service1.free_CA_mode, 0)
            service1_descriptors = service1.descriptors
            service1_desc1 = next(service1_descriptors)
            self.assertEqual(service1_desc1.descriptor_tag, 0x48)
            self.assertEqual(service1_desc1.service_type, 0x01)
            self.assertEqual(str(service1_desc1.service_provider_name), '')
            self.assertEqual(str(service1_desc1.service_name), 'TOKYO　MX1')
"""
            5C 38 F3 00 1D [
                48 0F (01 00 0C 1B 7E D4 CF CB D9
                       CF 21 21 CD D8 B1)
                CF 07 (01 FE 10 F0 06 00 01)
                C1 01 (84)]
            5C 39 F3 00 19 [
                48 0F (01 00 0C 1B 7E D4 CF CB D9
                       CF 21 21 CD D8 B1)
                CF 03 (02 FE 10)
                C1 01 (84)]
            5C 3A F3 00 1D [
                48 0F (01 00 0C 1B 7E D4 CF CB D9
                       CF 21 21 CD D8 B2)
                CF 07 (01 FE 11 F0 06 00 02)
                C1 01 (84)]
            5C 3F F1 00 20 [
                48 12 (A1 00 0F 1B 7E D4 CF CB D9 CF
                       21 21 CD D8 4E 57 3B 7E)
                CF 07 (01 FE 10 F0 06 00 01)
                C1 01 (84)]
            5D B8 E5 00 1F [
                48 10 (C0 00 0D 1B 7E CD D8 1B 7C EF
                       F3 BB B0 1B 7E B1)
                CF 08 (03 89 1B 7E CD D8 D4 D6)
                C1 01 (88)]
            5D
            47 20 11 12
               B9 E5 00 1F [
                48 10 (C0 00 0D 1B 7E CD D8 1B 7C EF
                       F3 BB B0 1B 7E B2)
                CF 08 (03 89 1B 7E CD D8 D4 D6)
                C1 01 (88)]
            2D 82 29 2B
"""
