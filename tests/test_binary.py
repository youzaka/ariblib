from unittest import TestCase

from ariblib import binary


class TestBinary(TestCase):

    def test_unhexlify(self):
        hexstring = '''
            47 60 00 1B 00 00 B0 1D 7E 87 D9 00 00 00 00 E0
            10 5C 38 E1 01 5C 39 E1 02 5D B8 FF C8 5D B9 FF
        '''
        expected = bytearray(
            b'\x47\x60\x00\x1B\x00\x00\xB0\x1D\x7E\x87\xD9\x00\x00\x00\x00\xE0'
            b'\x10\x5C\x38\xE1\x01\x5C\x39\xE1\x02\x5D\xB8\xFF\xC8\x5D\xB9\xFF'
        )
        self.assertEqual(binary.unhexlify(hexstring), expected)
