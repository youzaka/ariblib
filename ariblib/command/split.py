"""
ファイルの分割を行う

PATで最初に指定されるストリームのみ残す
```
$ python -m ariblib split --split SRC DST
```

"""

from argparse import FileType
from operator import itemgetter
import itertools
import os
import struct
import sys

from ariblib import packet, table, sections


def bits(data):
    masks = range(7, -1, -1)
    return ((x >> mask) & 0x01 for x, mask in itertools.product(data, masks))


def crc32(data):
    """CRC32を計算する"""

    crc = 0xFFFFFFFF
    for bit in bits(data):
        c = 1 if crc & 0x80000000 else 0
        crc <<= 1
        if c ^ bit:
            crc ^= 0x04c11db7
        crc &= 0xFFFFFFFF
    return crc


def replace_pat(pat):
    new_pat = bytearray(pat[:16])
    new_pat[2] = 0x11
    crc = crc32(new_pat)
    new_pat.extend(struct.pack('>L', crc))
    new_pat.extend([0xFF] * 163)
    return new_pat


def split_primary(args):
    """PMTで最初に指定されるストリームのみを残す"""

    remained_pids = set()
    with open(args.infile, 'rb') as f:
        payloads = packet.payloads(packet.packets(f))
        pat = next(table.tables([0x0], [0x0], payloads))
        # 置き換え後の新しいPAT
        new_pat = replace_pat(pat)
        remained_pmt_pid = next(
            a['program_map_pid'] for a in sections.program_associations(pat)
            if a['program_number'] != 0)
        remained_pids.add(remained_pmt_pid)
        pmt = next(table.tables([remained_pmt_pid], [0x2], payloads))
        program_maps = list(sections.program_maps(pmt))
        # PCRと最初のストリームのPIDを残す
        remained_pids.add(program_maps[0]['pcr_pid'])
        remained_pids.update(pm['elementary_pid'] for pm in program_maps
                             if pm['stream_type'] != 0x0D)

    # 実際のフィルタリング
    with open(args.infile, 'rb') as f, open(args.outfile, 'wb') as out:
        for p in packet.packets(f):
            this_pid = packet.pid(p)
            if this_pid == 0x0:
                out.write(p[:5])
                out.write(new_pat)
            elif this_pid in remained_pids:
                out.write(p)


def split_by_pmt(args):
    """PMT の version_nummber を検知してファイルを分割する"""

    # version_number を見る PMT の program_numberr と program_map_pid を取得
    with open(args.infile, 'rb') as f:
        payloads = packet.payloads(packet.packets(f))
        pat = next(table.tables([0x0], [0x0], payloads))
        associations = sections.program_associations(pat)
        pmt_number, pmt_pid = next(
            (a['program_number'], a['program_map_pid']) for a in associations
            if a['program_number'] != 0)
        pmt = next(table.tables([pmt_pid], [0x2], payloads))
        version_number = next(sections.program_maps(pmt))['version_number']

    # ファイル名を作成
    root, ext = os.path.splitext(args.infile)
    get_outfile = lambda v: "{}_{}{}".format(root, v, ext)
    outfile = get_outfile(version_number)
    outfiles = [outfile]

    # ファイルを分割して保存
    out = open(outfile, 'wb')
    with open(args.infile, 'rb') as f:
        for p in packet.packets(f):
            out.write(p)
            if (packet.pid(p) == pmt_pid and
                    packet.payload_unit_start_indicator(p)):
                pmt = next(sections.program_maps(packet.payload(p)[1]))
                if (pmt_number == pmt['program_number'] and
                        version_number != pmt['version_number']):
                    out.close()
                    version_number = pmt['version_number']
                    outfile = get_outfile(version_number)
                    outfiles.append(outfile)
                    out = open(outfile, 'wb')
    out.close()

    # ファイルサイズが最も大きいもののみ残し、それ以外は削除する
    main = max(outfiles, key=os.path.getsize)
    outfiles.remove(main)
    os.rename(main, args.outfile)
    for outfile in outfiles:
        os.unlink(outfile)


def add_parser(parsers):
    parser = parsers.add_parser('split')
    parser.add_argument(
        '--primary', action='store_const', dest='command',
        const=split_primary, default=split_primary,
        help='split primary stream')
    parser.add_argument(
        '--pmt', action='store_const', dest='command', const=split_by_pmt,
        help='split by pmt version number')
    parser.add_argument('infile')
    parser.add_argument('outfile')
