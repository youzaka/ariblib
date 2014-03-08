#!/usr/bin/env python3.2
# -*- coding: utf-8 -*-

import sys
import io

from ariblib.aribgaiji import *

"""
ARIB文字の実装クラス
original: https://github.com/murakamiy/epgdump_py/blob/master/aribstr.py
Copyright (C) 2011 Yasumasa Murakami. All Rights Reserved.
"""


class Code:
    (KANJI, ALPHANUMERIC, HIRAGANA, KATAKANA, MOSAIC_A, MOSAIC_B, MOSAIC_C,
     MOSAIC_D, PROP_ALPHANUMERIC, PROP_HIRAGANA, PROP_KATAKANA,
     JIS_X0201_KATAKANA, JIS_KANJI_PLANE_1, JIS_KANJI_PLANE_2,
     ADDITIONAL_SYMBOLS, UNSUPPORTED) = range(16)

CODE_SET_G = {
    0x42: (Code.KANJI, 2),
    0x4A: (Code.ALPHANUMERIC, 1),
    0x30: (Code.HIRAGANA, 1),
    0x31: (Code.KATAKANA, 1),
    0x32: (Code.MOSAIC_A, 1),
    0x33: (Code.MOSAIC_B, 1),
    0x34: (Code.MOSAIC_C, 1),
    0x35: (Code.MOSAIC_D, 1),
    0x36: (Code.PROP_ALPHANUMERIC, 1),
    0x37: (Code.PROP_HIRAGANA, 1),
    0x38: (Code.PROP_KATAKANA, 1),
    0x49: (Code.JIS_X0201_KATAKANA, 1),
    0x39: (Code.JIS_KANJI_PLANE_1, 2),
    0x3A: (Code.JIS_KANJI_PLANE_2, 2),
    0x3B: (Code.ADDITIONAL_SYMBOLS, 2),
}

CODE_SET_DRCS = {
    0x40: (Code.UNSUPPORTED, 2),  # DRCS-0
    0x41: (Code.UNSUPPORTED, 1),  # DRCS-1
    0x42: (Code.UNSUPPORTED, 1),  # DRCS-2
    0x43: (Code.UNSUPPORTED, 1),  # DRCS-3
    0x44: (Code.UNSUPPORTED, 1),  # DRCS-4
    0x45: (Code.UNSUPPORTED, 1),  # DRCS-5
    0x46: (Code.UNSUPPORTED, 1),  # DRCS-6
    0x47: (Code.UNSUPPORTED, 1),  # DRCS-7
    0x48: (Code.UNSUPPORTED, 1),  # DRCS-8
    0x49: (Code.UNSUPPORTED, 1),  # DRCS-9
    0x4A: (Code.UNSUPPORTED, 1),  # DRCS-10
    0x4B: (Code.UNSUPPORTED, 1),  # DRCS-11
    0x4C: (Code.UNSUPPORTED, 1),  # DRCS-12
    0x4D: (Code.UNSUPPORTED, 1),  # DRCS-13
    0x4E: (Code.UNSUPPORTED, 1),  # DRCS-14
    0x4F: (Code.UNSUPPORTED, 1),  # DRCS-15
    0x70: (Code.UNSUPPORTED, 1),  # MACRO
}

CODE_SET_KEYS = list(CODE_SET_DRCS.keys()) + list(CODE_SET_G.keys())

ARIB_BASE = {
    0x79: 0x3C,
    0x7A: 0x23,
    0x7B: 0x56,
    0x7C: 0x57,
    0x7D: 0x22,
    0x7E: 0x26,
}

ARIB_HIRAGANA_MAP = {
    0x77: 0x35,
    0x78: 0x36,
}

ARIB_KATAKANA_MAP = {
    0x77: 0x33,
    0x78: 0x34,
}

ARIB_KATAKANA_MAP.update(ARIB_BASE)
ARIB_HIRAGANA_MAP.update(ARIB_BASE)
# ひらがな  カタカナ
# ゝ 35     ヽ 33
# ゞ 36     ヾ 34
# ー 3c     ー 3c
# 。 23     。 23
# 「 56     「 56
# 」 57     」 57
# 、 22     、 22
# ・ 26     ・ 26

ESC_SEQ_ASCII = (0x1B, 0x28, 0x42)
ESC_SEQ_ZENKAKU = (0x1B, 0x24, 0x42)
ESC_SEQ_HANKAKU = (0x1B, 0x28, 0x49)


class Buffer:
    G0, G1, G2, G3 = range(4)


class CodeArea:
    LEFT, RIGHT = range(2)


class AribIndexError(Exception):
    pass


class EscapeSequenceError(Exception):
    pass


class DegignationError(Exception):
    pass


class CodeSetController:

    def __init__(self):
        self.v_buffer = {
            Buffer.G0: CODE_SET_G[0x42],  # KANJI
            Buffer.G1: CODE_SET_G[0x4a],  # ALPHANUMERIC
            Buffer.G2: CODE_SET_G[0x30],  # HIRAGANA
            Buffer.G3: CODE_SET_G[0x31],  # KATAKANA
        }
        self.single_shift = None
        self.graphic_left = Buffer.G0   # KANJI
        self.graphic_right = Buffer.G2  # HIRAGANA
        self.esc_seq_count = 0
        self.esc_buffer_index = Buffer.G0
        self.esc_drcs = False

    def degignate(self, code):
        if not code in CODE_SET_KEYS:
            raise DegignationError(
                'esc_seq_count=%i esc_buffer_index=%s code=0x%02X' % (
                    self.esc_seq_count, self.esc_buffer_index, code
                )
            )
        if self.esc_drcs:
            self.v_buffer[self.esc_buffer_index] = CODE_SET_DRCS[code]
        else:
            self.v_buffer[self.esc_buffer_index] = CODE_SET_G[code]
        self.esc_seq_count = 0

    def invoke(self, buffer_index, area, locking_shift=True):
        if CodeArea.LEFT == area:
            if locking_shift:
                self.graphic_left = buffer_index
            else:
                self.single_shift = buffer_index
        elif CodeArea.RIGHT == area:
            self.graphic_right = buffer_index
        self.esc_seq_count = 0

    def get_current_code(self, data):
        if 0x21 <= data <= 0x7E:
            if self.single_shift:
                code = self.v_buffer[self.single_shift]
                self.single_shift = None
                return code
            return self.v_buffer[self.graphic_left]
        elif 0xA1 <= data <= 0xFE:
            return self.v_buffer[self.graphic_right]
        return None

    def set_escape(self, buffer_index, drcs):
        if buffer_index is not None:
            self.esc_buffer_index = buffer_index
        self.esc_drcs = drcs
        self.esc_seq_count += 1


class AribArray(bytearray):
    esc_seq = None

    def pop0(self):
        try:
            return self.pop(0)
        except IndexError:
            raise AribIndexError

    def append_str(self, esc_seq, *string):
        if self.esc_seq != esc_seq:
            self.extend(esc_seq)
        self.esc_seq = esc_seq
        if len(string) > 1:
            self.extend(string)
        else:
            self.append(string[0])


class AribString:
    def __init__(self, array):
        self.control = CodeSetController()
        self.arib_array = AribArray(array)
        self.jis_array = AribArray()
        self.utf_buffer = io.StringIO()
        self.utf_buffer_symbol = io.StringIO()
        self.split_symbol = False

    def __add__(self, other):
        self.arib_array += other.arib_array
        return self

    def __str__(self):
        return self.convert_utf().rstrip()

    def __nonzero__(self):
        return not self.arib_array

    def convert_utf_split(self):
        self.split_symbol = True
        self.convert()
        self.flush_jis_array()
        return (self.utf_buffer.getvalue(), self.utf_buffer_symbol.getvalue())

    def convert_utf(self, with_gaiji=True):
        self.convert(with_gaiji)
        self.flush_jis_array()
        return self.utf_buffer.getvalue()

    def flush_jis_array(self):
        if len(self.jis_array) > 0:
            try:
                uni = self.jis_array.decode('iso-2022-jp')
            except UnicodeDecodeError:
                uni = 'UnicodeDecodeError'
            self.utf_buffer.write(uni)
            self.jis_array = AribArray()

    def convert(self, with_gaiji=True):
        while True:
            try:
                data = self.arib_array.pop0()
                if self.control.esc_seq_count:
                    self.do_escape(data)
                else:
                    if 0x21 <= data <= 0x7E or 0xA1 <= data <= 0xFE:
                        # GL/GR Table
                        self.do_convert(data, with_gaiji)
                    elif data in (
                            0x20,   # space
                            0xA0,   # space (arib)
                            0x09,  # HT
                    ):
                        self.jis_array.append_str(ESC_SEQ_ASCII, 0x20)
                    elif data in (
                            0x0D,  # CR
                            0x0A,  # LF
                    ):
                        self.jis_array.append_str(ESC_SEQ_ASCII, 0x0A)
                    else:
                         # Control Character
                        self.do_control(data)
            except AribIndexError:
                break
        return self.jis_array

    def do_convert(self, data, with_gaiji=True):
        code, size = self.control.get_current_code(data)
        char = data
        char2 = 0x0
        if size == 2:
            char2 = self.arib_array.pop0()
        if 0xA1 <= char <= 0xFE:
            char = char & 0x7F
            char2 = char2 & 0x7F

        if code in (
            Code.KANJI, Code.JIS_KANJI_PLANE_1, Code.JIS_KANJI_PLANE_2
        ):
            # 漢字コード出力
            self.jis_array.append_str(ESC_SEQ_ZENKAKU, char, char2)
        elif code in (Code.ALPHANUMERIC, Code.PROP_ALPHANUMERIC):
            # 英数字コード出力
            self.jis_array.append_str(ESC_SEQ_ASCII, char)
        elif code in (Code.HIRAGANA, Code.PROP_HIRAGANA):
            # ひらがなコード出力
            if char >= 0x77:
                self.jis_array.append_str(
                    ESC_SEQ_ZENKAKU, 0x21, ARIB_HIRAGANA_MAP[char])
            else:
                self.jis_array.append_str(
                    ESC_SEQ_ZENKAKU, 0x24, char)
        elif code in (Code.PROP_KATAKANA, Code.KATAKANA):
            # カタカナコード出力
            if char >= 0x77:
                self.jis_array.append_str(
                    ESC_SEQ_ZENKAKU, 0x21, ARIB_KATAKANA_MAP[char])
            else:
                self.jis_array.append_str(ESC_SEQ_ZENKAKU, 0x25, char)
        elif code == Code.JIS_X0201_KATAKANA:
            # 半角カタカナコード出力
            self.jis_array.append_str(ESC_SEQ_HANKAKU, char)
        elif code == Code.ADDITIONAL_SYMBOLS:
            # 追加シンボル文字コード出力
            self.flush_jis_array()
            if with_gaiji:
                if self.split_symbol:
                    wchar = ((char << 8) + char2)
                    gaiji = GAIJI_MAP_TITLE.get(wchar)
                    if gaiji is not None:
                        self.utf_buffer_symbol.write(gaiji)
                    else:
                        self.utf_buffer.write(GAIJI_MAP_OTHER.get(wchar, "??"))
                else:
                    self.utf_buffer.write(
                        GAIJI_MAP.get(((char << 8) + char2), "??"))

    def do_control(self, data):
        if data == 0x0F:
            self.control.invoke(Buffer.G0, CodeArea.LEFT, True)   # LS0
        elif data == 0x0E:
            self.control.invoke(Buffer.G1, CodeArea.LEFT, True)   # LS1
        elif data == 0x19:
            self.control.invoke(Buffer.G2, CodeArea.LEFT, False)  # SS2
        elif data == 0x1D:
            self.control.invoke(Buffer.G3, CodeArea.LEFT, False)  # SS3
        elif data == 0x1B:
            self.control.esc_seq_count = 1

    def do_escape(self, data):
        if self.control.esc_seq_count == 1:
            if data == 0x6E:
                self.control.invoke(Buffer.G2, CodeArea.LEFT, True)   # LS2
            elif data == 0x6F:
                self.control.invoke(Buffer.G3, CodeArea.LEFT, True)   # LS3
            elif data == 0x7E:
                self.control.invoke(Buffer.G1, CodeArea.RIGHT, True)  # LS1R
            elif data == 0x7D:
                self.control.invoke(Buffer.G2, CodeArea.RIGHT, True)  # LS2R
            elif data == 0x7C:
                self.control.invoke(Buffer.G3, CodeArea.RIGHT, True)  # LS3R
            elif data in (0x24, 0x28):
                self.control.set_escape(Buffer.G0, False)
            elif data == 0x29:
                self.control.set_escape(Buffer.G1, False)
            elif data == 0x2A:
                self.control.set_escape(Buffer.G2, False)
            elif data == 0x2B:
                self.control.set_escape(Buffer.G3, False)
            else:
                raise EscapeSequenceError('esc_seq_count=%i data=0x%02X' % (
                    self.control.esc_seq_count, data,
                ))
        elif self.control.esc_seq_count == 2:
            if data == 0x20:
                self.control.set_escape(None, True)
            elif data == 0x28:
                self.control.set_escape(Buffer.G0, False)
            elif data == 0x29:
                self.control.set_escape(Buffer.G1, False)
            elif data == 0x2A:
                self.control.set_escape(Buffer.G2, False)
            elif data == 0x2B:
                self.control.set_escape(Buffer.G3, False)
            else:
                self.control.degignate(data)
        elif self.control.esc_seq_count == 3:
            if data == 0x20:
                self.control.set_escape(None, True)
            else:
                self.control.degignate(data)
        elif self.control.esc_seq_count == 4:
            self.control.degignate(data)

    def __repr__(self):
        return self.convert_utf().rstrip()

if __name__ == '__main__':
    f = open(sys.argv[1], 'rb')
    f.seek(0, 2)
    byte = f.tell()
    f.seek(0)
    arr = array.array('B')
    arr.fromfile(f, byte)
    f.close()

    arib = AribString(arr)
    arib.convert()

    f = open("output.txt", 'wb')
    arib.jis_array.tofile(f)
    f.close()
