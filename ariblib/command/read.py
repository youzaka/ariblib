from ariblib import tsopen
from ariblib.sections import ProgramAssociationSection, ProgramMapSection


def read(args):
    with tsopen(args.path) as ts:
        pat = next(ts.sections(ProgramAssociationSection))
        pmt_pids = [pid.program_map_PID for pid in pat.pids
                    if pid.program_number != 0]
        ProgramMapSection.__pids__ = pmt_pids
        for pmt in ts.sections(ProgramMapSection):
            print(pmt._packet)
            for item in pmt.maps:
                print(item.stream_type, item.elementary_PID)
                for desc in item.descriptors:
                    print(">", desc.descriptor_tag)


def add_parser(parsers):
    parser = parsers.add_parser('read', help='read ts file')
    parser.set_defaults(command=read)
    parser.add_argument('path', help='ts file path')
