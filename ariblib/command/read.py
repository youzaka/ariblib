import binascii
import re

from ariblib import packet, tsopen
from ariblib.sections import NetworkInformationSection


def read(args):
    with tsopen(args.path) as ts:
        for p in ts:
            if packet.pid(p) in NetworkInformationSection.__pids__:
                spaced = re.sub(r'([0-9a-f][0-9a-f])', r'\1 ',
                                binascii.hexlify(p).decode())
                feeded = re.sub(r'((?:[0-9a-f][0-9a-f] ){16})', '\\1\n', spaced)
                print(feeded.upper())


def add_parser(parsers):
    parser = parsers.add_parser('read', help='read ts file')
    parser.set_defaults(command=read)
    parser.add_argument('path', help='ts file path')
