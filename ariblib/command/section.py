"""
セクションのパース確認用スクリプト
"""

from argparse import FileType
import json
import sys

from ariblib import packet, sections, table


def parse_pat(args):
    payloads = packet.payloads(packet.packets(args.infile))
    pat = next(table.tables([0x0], [0x0], payloads))
    associations = list(sections.program_associations(pat))
    json.dump(associations, args.outfile, indent=4)


def parse_pmt(args):
    payloads = packet.payloads(packet.packets(args.infile))
    pat = next(table.tables([0x0], [0x0], payloads))
    associations = list(sections.program_associations(pat))
    pmt_pids = [association['program_map_pid'] for association
                in sections.program_associations(pat)
                if association['program_number'] != 0]
    pmt = next(table.tables(pmt_pids, [0x2], payloads))
    program_maps = list(sections.program_maps(pmt))
    json.dump(program_maps, args.outfile, indent=4)


def parse_nit(args):
    payloads = packet.payloads(packet.packets(args.infile))
    nit = next(table.tables([0x10], [0x40, 0x41], payloads))
    networks = list(sections.network_informations(nit))
    json.dump(networks, args.outfile, indent=4)


def parse_sdt(args):
    payloads = packet.payloads(packet.packets(args.infile))
    sdt = next(table.tables([0x11], [0x42, 0x46], payloads))
    services = list(sections.service_descriptions(sdt))
    json.dump(services, args.outfile, indent=4)


def add_parser(parsers):
    parser = parsers.add_parser('section')
    parser.add_argument(
        '--pat', action='store_const', dest='command', const=parse_pat,
        help='parse pat')
    parser.add_argument(
        '--pmt', action='store_const', dest='command', const=parse_pmt,
        help='parse pmt')
    parser.add_argument(
        '--nit', action='store_const', dest='command', const=parse_nit,
        help='parse nit')
    parser.add_argument(
        '--sdt', action='store_const', dest='command', const=parse_sdt,
        help='parse sdt')
    parser.add_argument(
        'infile', nargs='?', type=FileType('rb'), default=sys.stdin)
    parser.add_argument(
        'outfile', nargs='?', type=FileType('w'), default=sys.stdout)
