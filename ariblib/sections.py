from ariblib.mnemonics import bslbf, loop, rpchof, uimsbf
from ariblib.syntax import Syntax


class Section(Syntax):

    __table_ids__ = range(256)

    def __init__(self, packet):
        Syntax.__init__(self, packet)


class ProgramAssociationSection(Section):

    """Program Association Section : PAT (ISO 13818-1 2.4.4.3)"""

    __pids__ = [0x00]
    __table_ids__ = [0x00]

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use = bslbf(1)
    reserved_1 = bslbf(2)
    section_length = uimsbf(12)
    transport_stream_id = uimsbf(16)
    reserved_2 = bslbf(2)
    version_number = uimsbf(5)
    current_next_indicator = bslbf(1)
    section_number = uimsbf(8)
    last_section_number = uimsbf(8)

    @loop(section_length - 9)
    class pids(Syntax):
        program_number = uimsbf(16)
        reserved = bslbf(3)
        program_map_PID = uimsbf(13)

    CRC_32 = rpchof(32)

    @property
    def pmt_maps(self):
        for pid in self.pids:
            if pid.program_number != 0:
                yield pid.program_number, pid.program_map_PID

    @property
    def pmt_pids(self):
        for number, pid in self.pmt_maps:
            yield pid

    @property
    def network_pid(self):
        for pid in self.pids:
            if pid.program_number == 0:
                return pid.program_map_PID
