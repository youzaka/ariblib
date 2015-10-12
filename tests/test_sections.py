from io import BytesIO
from unittest import TestCase

from ariblib import tsopen
from ariblib.binary import unhexlify
from ariblib.sections import ProgramAssociationSection, ProgramMapSection


class TestProgramAssociationSection(TestCase):

    def test_pat(self):
        packet = '''
            47 60 00 1B 00 00 B0 1D 7E 87 D9 00 00 00 00 E0
            10 5C 38 E1 01 5C 39 E1 02 5D B8 FF C8 5D B9 FF
            C9 90 3F 0A 85 FF FF FF FF FF FF FF FF FF FF FF
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
            pat = next(ts.sections(ProgramAssociationSection))
            self.assertEqual(pat.table_id, 0)
            self.assertTrue(pat.section_syntax_indicator)
            self.assertEqual(pat.section_length, 29)
            self.assertEqual(pat.transport_stream_id, 0x7E87)
            self.assertEqual(pat.version_number, 0x0C)
            self.assertTrue(pat.current_next_indicator)
            self.assertEqual(pat.section_number, 0)
            self.assertEqual(pat.last_section_number, 0)
            self.assertEqual(pat.CRC_32, 0x903F0A85)

            self.assertEqual(pat.network_pid, 0x10)
            pmt_numbers = [0x5C38, 0x5C39, 0x5DB8, 0x5DB9]
            pmt_pids = [0x101, 0x102, 0x1FC8, 0x1FC9]
            self.assertEqual(list(pat.pmt_maps),
                             list(zip(pmt_numbers, pmt_pids)))
            self.assertEqual(list(pat.pmt_pids), pmt_pids)


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
