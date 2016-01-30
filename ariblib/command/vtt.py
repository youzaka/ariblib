from datetime import datetime, timedelta
from hashlib import md5
import os.path
import sys

from ariblib import tsopen
from ariblib.caption import WebVTTCProfileString
from ariblib.packet import SynchronizedPacketizedElementaryStream
from ariblib.sections import TimeOffsetSection
from ariblib.mnemonics import hexdump


def vtt(args):
    if args.outpath == '-':
        outpath = sys.stdout.fileno()
    else:
        outpath = args.outpath
    with tsopen(args.inpath) as ts, open(outpath, 'w') as out:
        SynchronizedPacketizedElementaryStream._pids = [ts.get_caption_pid()]

        base_pcr = next(ts.pcrs())
        base_time = next(ts.sections(TimeOffsetSection)).JST_time

        out.write('WEBVTT\n\n')
        number = 1
        base_date = datetime(2000, 1, 1)
        #fixme: DRCS処理を隠蔽して字幕文字オブジェクトだけ返すラッパークラスが必要
        # for caption in ts.captions(drcs=True, color=True):
        #     print(caption.datetime, caption.body) みたいな
        prev_caption_date = None
        prev_caption = ''
        for spes in ts.sections(SynchronizedPacketizedElementaryStream):
            caption_date = base_date + (spes.pts - base_pcr)
            for data in spes.data_units:
                if data.data_unit_parameter == 0x20:
                    caption = WebVTTCProfileString(data.data_unit_data)
                    if prev_caption_date:
                        out.write('{}\n{}.{:03d} --> {}.{:03d}\n{}\n\n'.format(
                            number, prev_caption_date.strftime('%H:%M:%S'),
                            prev_caption_date.microsecond // 1000,
                            caption_date.strftime('%H:%M:%S'),
                            caption_date.microsecond // 1000,
                            prev_caption))
                    number += 1
                    prev_caption_date = caption_date
                    prev_caption = caption
        if prev_caption:
            out.write('{}\n{}.{:03d} --> {}.{:03d}\n{}\n\n'.format(
                number, prev_caption_date.strftime('%H:%M:%S'),
                prev_caption_date.microsecond // 1000,
                caption_date.strftime('%H:%M:%S'),
                caption_date.microsecond // 1000,
                prev_caption))


def add_parser(parsers):
    parser = parsers.add_parser('vtt')
    parser.set_defaults(command=vtt)
    parser.add_argument('inpath', help='input file path')
    parser.add_argument('outpath', help='output file path')
