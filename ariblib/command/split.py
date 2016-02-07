from ariblib import packet, tsopen
from ariblib.sections import ProgramAssociationSection, ProgramMapSection

def crc32(data):
    """CRC32を計算する"""

    crc = 0xFFFFFFFF
    for x in data:
        for i in range(8):
            bit = (x >> (7 - i)) & 0x1
            c = 1 if crc & 0x80000000 else 0
            crc = crc << 1
            if c ^ bit:
                crc ^= 0x04c11db7
            crc &= 0xFFFFFFFF
    return crc


def replace_pat(pat):
    new_pat = bytearray(pat[:16])
    new_pat[2] = 0x11
    crc = crc32(new_pat)
    new_pat.append((crc >> 24) & 0xFF)
    new_pat.append((crc >> 16) & 0xFF)
    new_pat.append((crc >> 8) & 0xFF)
    new_pat.append(crc & 0xFF)
    new_pat.extend([0xFF] * 163)
    return new_pat


def split(args):
    """必要なストリームのみ残す"""

    remained_pids = set()
    with tsopen(args.inpath) as ts:
        pat = next(ts.sections(ProgramAssociationSection))
        # 置き換え後の新しいPAT
        new_pat = replace_pat(pat._packet)
        remained_pmt_pid = next(pat.pmt_pids)
        remained_pids.add(remained_pmt_pid)
        ProgramMapSection._pids = [remained_pmt_pid]
        pmt = next(ts.sections(ProgramMapSection))
        # PCRと最初のストリームのPIDを残す
        remained_pids.add(pmt.PCR_PID)
        remained_pids.update(pmt_map.elementary_PID for pmt_map in pmt.maps
                             if pmt_map.stream_type != 0x0d)

    pat_pid = ProgramAssociationSection._pids[0]
    with tsopen(args.inpath) as ts, open(args.outpath, 'wb') as out:
        for p in ts:
            if packet.pid(p) == pat_pid:
                out.write(p[:5])
                out.write(new_pat)
            elif packet.pid(p) in remained_pids:
                out.write(p)


def add_parser(parsers):
    parser = parsers.add_parser('split')
    parser.set_defaults(command=split)
    parser.add_argument('inpath', help='input file path')
    parser.add_argument('outpath', help='output file path')
