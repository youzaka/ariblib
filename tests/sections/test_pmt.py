from io import BytesIO
from unittest import TestCase

from ariblib import tsopen
from ariblib.binary import unhexlify
from ariblib.sections import ProgramMapSection


class TestProgramMapSection(TestCase):

    def test_pmt(self):
        packet = '''
            47 61 01 1E 00 02 B0 C7 5C 38 D1 00 00 E1 00 F0
            09 09 04 00 05 E0 31 C1 01 84 02 E1 21 F0 06 52
            01 00 C8 01 53 0F E1 12 F0 03 52 01 10 0D E7 40
            F0 0F 52 01 40 FD 0A 00 0C 33 3F 00 03 00 03 FF
            BF 0D E7 50 F0 0A 52 01 50 FD 05 00 0C 1F FF BF
            0D E7 51 F0 0A 52 01 51 FD 05 00 0C 1F FF BF 0D
            E7 52 F0 0A 52 01 52 FD 05 00 0C 1F FF BF 0D E9
            60 F0 0A 52 01 60 FD 05 00 0C 1F FF BF 0D E9 61
            F0 0A 52 01 61 FD 05 00 0C 1F FF BF 0D E7 5E F0
            10 52 01 5E 09 04 00 05 FF FF FD 05 00 0C 1F FF
            BF 0D E7 5F F0 10 52 01 5F 09 04 00 05 FF FF FD
            05 00 0C 1F FF BF 0D E9 6E F0 10 52
            47 21 01 1F 01 6E 09 04 00 05 FF FF FD 05 00 0C
            1F FF BF 32 23 3E 76 FF FF FF FF FF FF FF FF FF
            FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
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
        ProgramMapSection.__pids__ = [0x101, 0x102, 0x1FC8, 0x1FC9]
        with tsopen(unhexlify(packet)) as ts:
            pmt = next(ts.sections(ProgramMapSection))
            self.assertEqual(pmt.section_length, 199)
            self.assertEqual(pmt.program_number, 0x5C38)
            self.assertEqual(pmt.section_number, 0)
            self.assertEqual(pmt.last_section_number, 0)
            self.assertEqual(pmt.PCR_PID, 0x100)

            descriptors = pmt.descriptors
            desc1 = next(descriptors)
            self.assertEqual(desc1.descriptor_tag, 0x09)
            self.assertEqual(desc1.CA_system_ID, 0x05)
            self.assertEqual(desc1.CA_PID, 0x31)

            desc2 = next(descriptors)
            self.assertEqual(desc2.descriptor_tag, 0xC1)
            self.assertEqual(desc2.digital_recording_control_data, 2)
            self.assertFalse(desc2.maximum_bitrate_flag)
            self.assertFalse(desc2.component_control_flag)
            self.assertEqual(desc2.copy_control_type, 1)
            self.assertEqual(desc2.APS_control_data, 0)
            with self.assertRaises(StopIteration):
                next(descriptors)

            maps = pmt.maps
            map1 = next(maps)
            self.assertEqual(map1.stream_type, 0x02)
            self.assertEqual(map1.elementary_PID, 0x121)
            map1_descriptors = map1.descriptors
            map1_desc1 = next(map1_descriptors)
            self.assertEqual(map1_desc1.descriptor_tag, 0x52)
            self.assertEqual(map1_desc1.component_tag, 0x0)
            map1_desc2 = next(map1_descriptors)
            self.assertEqual(map1_desc2.descriptor_tag, 0xC8)
            self.assertFalse(map1_desc2.still_picture_flag)
            self.assertTrue(map1_desc2.sequence_end_code_flag)
            self.assertEqual(map1_desc2.video_encode_format, 4)
            with self.assertRaises(StopIteration):
                next(map1_descriptors)

            map2 = next(maps)
            self.assertEqual(map2.stream_type, 0x0F)
            self.assertEqual(map2.elementary_PID, 0x112)
            map2_descriptors = map2.descriptors
            map2_desc1 = next(map2_descriptors)
            self.assertEqual(map2_desc1.descriptor_tag, 0x52)
            self.assertEqual(map2_desc1.component_tag, 0x10)
            with self.assertRaises(StopIteration):
                next(map2_descriptors)

            map3 = next(maps)
            self.assertEqual(map3.stream_type, 0x0D)
            self.assertEqual(map3.elementary_PID, 0x740)
            map3_descriptors = map3.descriptors
            map3_desc1 = next(map3_descriptors)
            self.assertEqual(map3_desc1.descriptor_tag, 0x52)
            self.assertEqual(map3_desc1.component_tag, 0x40)
            map3_desc2 = next(map3_descriptors)
            self.assertEqual(map3_desc2.descriptor_tag, 0xFD)
            self.assertEqual(map3_desc2.data_component_id, 0x0C)
            self.assertEqual(map3_desc2.additional_data_component_info,
                             0x333F00030003FFBF)
            with self.assertRaises(StopIteration):
                next(map3_descriptors)

            map4 = next(maps)
            self.assertEqual(map4.stream_type, 0x0D)
            self.assertEqual(map4.elementary_PID, 0x750)
            map4_descriptors = map4.descriptors
            map4_desc1 = next(map4_descriptors)
            self.assertEqual(map4_desc1.descriptor_tag, 0x52)
            self.assertEqual(map4_desc1.component_tag, 0x50)
            map4_desc2 = next(map4_descriptors)
            self.assertEqual(map4_desc2.descriptor_tag, 0xFD)
            self.assertEqual(map4_desc2.data_component_id, 0x0C)
            self.assertEqual(map4_desc2.additional_data_component_info,
                             0x1FFFBF)
            with self.assertRaises(StopIteration):
                next(map4_descriptors)

            map5 = next(maps)
            self.assertEqual(map5.stream_type, 0x0D)
            self.assertEqual(map5.elementary_PID, 0x751)
            map5_descriptors = map5.descriptors
            map5_desc1 = next(map5_descriptors)
            self.assertEqual(map5_desc1.descriptor_tag, 0x52)
            self.assertEqual(map5_desc1.component_tag, 0x51)
            map5_desc2 = next(map5_descriptors)
            self.assertEqual(map5_desc2.descriptor_tag, 0xFD)
            self.assertEqual(map5_desc2.data_component_id, 0x0C)
            self.assertEqual(map5_desc2.additional_data_component_info,
                             0x1FFFBF)
            with self.assertRaises(StopIteration):
                next(map5_descriptors)

            map6 = next(maps)
            self.assertEqual(map6.stream_type, 0x0D)
            self.assertEqual(map6.elementary_PID, 0x752)
            map6_descriptors = map6.descriptors
            map6_desc1 = next(map6_descriptors)
            self.assertEqual(map6_desc1.descriptor_tag, 0x52)
            self.assertEqual(map6_desc1.component_tag, 0x52)
            map6_desc2 = next(map6_descriptors)
            self.assertEqual(map6_desc2.descriptor_tag, 0xFD)
            self.assertEqual(map6_desc2.data_component_id, 0x0C)
            self.assertEqual(map6_desc2.additional_data_component_info,
                             0x1FFFBF)
            with self.assertRaises(StopIteration):
                next(map6_descriptors)

            map7 = next(maps)
            self.assertEqual(map7.stream_type, 0x0D)
            self.assertEqual(map7.elementary_PID, 0x960)
            map7_descriptors = map7.descriptors
            map7_desc1 = next(map7_descriptors)
            self.assertEqual(map7_desc1.descriptor_tag, 0x52)
            self.assertEqual(map7_desc1.component_tag, 0x60)
            map7_desc2 = next(map7_descriptors)
            self.assertEqual(map7_desc2.descriptor_tag, 0xFD)
            self.assertEqual(map7_desc2.data_component_id, 0x0C)
            self.assertEqual(map7_desc2.additional_data_component_info,
                             0x1FFFBF)
            with self.assertRaises(StopIteration):
                next(map7_descriptors)

            map8 = next(maps)
            self.assertEqual(map8.stream_type, 0x0D)
            self.assertEqual(map8.elementary_PID, 0x961)
            map8_descriptors = map8.descriptors
            map8_desc1 = next(map8_descriptors)
            self.assertEqual(map8_desc1.descriptor_tag, 0x52)
            self.assertEqual(map8_desc1.component_tag, 0x61)
            map8_desc2 = next(map8_descriptors)
            self.assertEqual(map8_desc2.descriptor_tag, 0xFD)
            self.assertEqual(map8_desc2.data_component_id, 0x0C)
            self.assertEqual(map8_desc2.additional_data_component_info,
                             0x1FFFBF)
            with self.assertRaises(StopIteration):
                next(map8_descriptors)

            map9 = next(maps)
            self.assertEqual(map9.stream_type, 0x0D)
            self.assertEqual(map9.elementary_PID, 0x75E)
            map9_descriptors = map9.descriptors
            map9_desc1 = next(map9_descriptors)
            self.assertEqual(map9_desc1.descriptor_tag, 0x52)
            self.assertEqual(map9_desc1.component_tag, 0x5E)
            map9_desc2 = next(map9_descriptors)
            self.assertEqual(map9_desc2.descriptor_tag, 0x09)
            self.assertEqual(map9_desc2.CA_system_ID, 0x05)
            self.assertEqual(map9_desc2.CA_PID, 0x1FFF)
            map9_desc3 = next(map9_descriptors)
            self.assertEqual(map9_desc3.descriptor_tag, 0xFD)
            self.assertEqual(map9_desc3.data_component_id, 0x0C)
            self.assertEqual(map9_desc3.additional_data_component_info,
                             0x1FFFBF)
            with self.assertRaises(StopIteration):
                next(map9_descriptors)

            map10 = next(maps)
            self.assertEqual(map10.stream_type, 0x0D)
            self.assertEqual(map10.elementary_PID, 0x75F)
            map10_descriptors = map10.descriptors
            map10_desc1 = next(map10_descriptors)
            self.assertEqual(map10_desc1.descriptor_tag, 0x52)
            self.assertEqual(map10_desc1.component_tag, 0x5F)
            map10_desc2 = next(map10_descriptors)
            self.assertEqual(map10_desc2.descriptor_tag, 0x09)
            self.assertEqual(map10_desc2.CA_system_ID, 0x05)
            self.assertEqual(map10_desc2.CA_PID, 0x1FFF)
            map10_desc3 = next(map10_descriptors)
            self.assertEqual(map10_desc3.descriptor_tag, 0xFD)
            self.assertEqual(map10_desc3.data_component_id, 0x0C)
            self.assertEqual(map10_desc3.additional_data_component_info,
                             0x1FFFBF)
            with self.assertRaises(StopIteration):
                next(map10_descriptors)

            map11 = next(maps)
            self.assertEqual(map11.stream_type, 0x0D)
            self.assertEqual(map11.elementary_PID, 0x96E)
            map11_descriptors = map11.descriptors
            map11_desc1 = next(map11_descriptors)
            self.assertEqual(map11_desc1.descriptor_tag, 0x52)
            self.assertEqual(map11_desc1.component_tag, 0x6E)
            map11_desc2 = next(map11_descriptors)
            self.assertEqual(map11_desc2.descriptor_tag, 0x09)
            self.assertEqual(map11_desc2.CA_system_ID, 0x05)
            self.assertEqual(map11_desc2.CA_PID, 0x1FFF)
            map11_desc3 = next(map11_descriptors)
            self.assertEqual(map11_desc3.descriptor_tag, 0xFD)
            self.assertEqual(map11_desc3.data_component_id, 0x0C)
            self.assertEqual(map11_desc3.additional_data_component_info,
                             0x1FFFBF)
            with self.assertRaises(StopIteration):
                next(map11_descriptors)

            with self.assertRaises(StopIteration):
                next(maps)
