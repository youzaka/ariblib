from io import BytesIO
from unittest import TestCase

from ariblib import tsopen
from ariblib.sections import ProgramAssociationSection


class TestProgramAssociationSection(TestCase):

    def test_pat(self):
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
            pat = next(ts.sections(ProgramAssociationSection))
            self.assertEqual(pat.table_id, 0)
            self.assertTrue(pat.section_syntax_indicator)
            self.assertEqual(pat.section_length, 29)
            self.assertEqual(pat.transport_stream_id, 0x7FE3)
            self.assertEqual(pat.version_number, 0x13)
            self.assertTrue(pat.current_next_indicator)
            self.assertEqual(pat.section_number, 0)
            self.assertEqual(pat.last_section_number, 0)
            self.assertEqual(pat.CRC_32, 0xAFD541AE)

            pids = [(pid.program_number, pid.program_map_PID) for pid
                    in pat.pids]
            expecteds = [(0, 16), (1048, 257), (1049, 258), (1432, 8136),
                         (1183, 2032)]
            self.assertEqual(pids, expecteds)
