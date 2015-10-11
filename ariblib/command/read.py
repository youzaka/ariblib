from ariblib import tsopen


def read(args):
    with tsopen(args.path) as ts:
        for packet in ts:
            print(packet)


def add_parser(parsers):
    parser = parsers.add_parser('read', help='read ts file')
    parser.set_defaults(command=read)
    parser.add_argument('path', help='ts file path')
