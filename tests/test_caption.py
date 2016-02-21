from datetime import timedelta
from unittest import TestCase

from ariblib import caption


class TestCaption(TestCase):

    def test_srt_timestamp(self):
        pts = 8073051319
        pts_hz = 90000
        second = pts / pts_hz
        delta = timedelta(seconds=second)
        expected = '24:55:00,570'
        self.assertEqual(caption.srt_timestamp(delta), expected)

    def test_case2(self):
        pts = 8589934591
        pts_hz = 90000
        second = pts / pts_hz
        delta = timedelta(seconds=second)
        expected = '26:30:43,717'
        self.assertEqual(caption.srt_timestamp(delta), expected)
