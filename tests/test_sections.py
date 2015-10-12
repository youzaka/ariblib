from io import BytesIO
from unittest import TestCase

from ariblib import tsopen
from ariblib.binary import unhexlify
from ariblib.sections import ProgramAssociationSection


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
