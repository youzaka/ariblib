from ariblib.descriptors import descriptors
from ariblib.mnemonics import bslbf, loop, rpchof, uimsbf
from ariblib.syntax import Syntax


class Section(Syntax):

    __table_ids__ = range(256)

    def __init__(self, packet):
        Syntax.__init__(self, packet)

    def isfull(self):
        return self.section_length <= len(self) + 3


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


class ProgramMapSection(Section):

    """Program Map Section : PMT (ISO 13818-1 2.4.4.8)"""

    __table_ids__ = [0x02]

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use = bslbf(1)
    reserved_1 = bslbf(2)
    section_length = uimsbf(12)
    program_number = uimsbf(16)
    reserved_2 = bslbf(2)
    version_number = uimsbf(5)
    current_next_indicator = bslbf(1)
    section_number = uimsbf(8)
    last_section_number = uimsbf(8)
    reserved_3 = bslbf(3)
    PCR_PID = uimsbf(13)
    reserved_4 = bslbf(4)
    program_info_length = uimsbf(12)
    descriptors = descriptors(program_info_length)

    @loop(section_length - (program_info_length + 13))
    class maps(Syntax):
        stream_type = uimsbf(8)
        reserved_1 = bslbf(3)
        elementary_PID = uimsbf(13)
        reserved_2 = bslbf(4)
        ES_info_length = uimsbf(12)
        descriptors = descriptors(ES_info_length)

    CRC_32 = rpchof(32)


class NetworkInformationSection(Section):

    """ネットワーク情報セクション NIT (ARIB-STD-B10-2-5.2.4)"""

    __pids__ = [0x10]
    __table_ids__ = [0x40, 0x41]

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use_1 = bslbf(1)
    reserved_1 = bslbf(2)
    section_length = uimsbf(12)
    network_id = uimsbf(16)
    reserved_2 = bslbf(2)
    version_number = uimsbf(5)
    current_next_indicator = bslbf(1)
    section_number = uimsbf(8)
    last_section_number = uimsbf(8)
    reserved_future_use_2 = bslbf(4)
    network_descriptors_length = uimsbf(12)
    network_descriptors = descriptors(network_descriptors_length)
    reserved_future_use_3 = bslbf(4)
    transport_stream_loop_length = uimsbf(12)

    @loop(transport_stream_loop_length)
    class transport_streams(Syntax):
        transport_stream_id = uimsbf(16)
        original_network_id = uimsbf(16)
        reserved_future_use = bslbf(4)
        transport_descriptors_length = uimsbf(12)
        descriptors = descriptors(transport_descriptors_length)

    CRC_32 = rpchof(32)


class ServiceDescriptionSection(Section):

    """サービス記述セクション SDT (ARIB-STD-B10-2-5.2.6)"""

    __pids__ = [0x11]
    __table_ids__ = [0x42, 0x46]

    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use_1 = bslbf(1)
    reserved_1 = bslbf(2)
    section_length = uimsbf(12)
    transport_stream_id = uimsbf(16)
    reserved_2 = bslbf(2)
    version_number = uimsbf(5)
    current_next_indicator = bslbf(1)
    section_number = uimsbf(8)
    last_section_number = uimsbf(8)
    original_network_id = uimsbf(16)
    reserved_future_use_2 = bslbf(8)

    @loop(section_length - 12)
    class services(Syntax):
        service_id = uimsbf(16)
        reserved_future_use = bslbf(3)
        EIT_user_defined_flags = bslbf(3)
        EIT_schedule_flag = bslbf(1)
        EIT_present_following_flag = bslbf(1)
        running_status = uimsbf(3)
        free_CA_mode = bslbf(1)
        descriptors_loop_length = uimsbf(12)
        descriptors = descriptors(descriptors_loop_length)

    CRC_32 = rpchof(32)
