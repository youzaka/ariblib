from ariblib.descriptors import descriptors
from ariblib import parse


def program_associations(p):
    """PATのパースを行う"""

    table_id = p[0]
    section_length = ((p[1] & 0x0F) << 8) | p[2]
    transport_stream_id = (p[3] << 8) | p[4]
    version_number = (p[5] & 0x3E) >> 1
    section_number = p[6]
    last_section_number = p[7]

    start = 8
    end = section_length - 4
    while start < end:
        program_number = (p[start] << 8) | p[start+1]
        program_map_pid = ((p[start+2] & 0x1F) << 8) | p[start+3]
        yield {
            'table_id': table_id,
            'transport_stream_id': transport_stream_id,
            'version_number': version_number,
            'section_number': section_number,
            'last_section_number': last_section_number,
            'program_number': program_number,
            'program_map_pid': program_map_pid,
        }
        start += 4


def program_maps(p):
    """PMTのパースを行う"""

    table_id = p[0]
    section_length = ((p[1] & 0x0F) << 8) | p[2]
    program_number = (p[3] << 8) | p[4]
    version_number = (p[5] & 0x3E) >> 1
    section_number = p[6]
    last_section_number = p[7]
    pcr_pid = ((p[8] & 0x1F) << 8) | p[9]
    program_info_length = ((p[10] & 0x0F) << 8) | p[11]

    base = {
        'table_id': table_id,
        'program_number': program_number,
        'version_number': version_number,
        'section_number': section_number,
        'last_section_number': last_section_number,
        'pcr_pid': pcr_pid,
    }
    base.update(descriptors(p[12:12+program_info_length]))

    start = 12 + program_info_length
    end = section_length - 4
    while start < end:
        stream_type = p[start]
        elementary_pid = ((p[start+1] & 0x1F) << 8) | p[start+2]
        es_info_length = ((p[start+3] & 0x0F) << 8) | p[start+4]
        additional = {
            'stream_type': stream_type,
            'elementary_pid': elementary_pid,
        }
        additional.update(descriptors(p[start+5:start+5+es_info_length]))

        yield dict(base, **additional)
        start += 5 + es_info_length


def network_informations(p):
    """NITのパースを行う"""

    table_id = p[0]
    section_length = ((p[1] & 0x0F) << 8) | p[2]
    network_id = (p[3] << 8) | p[4]
    version_number = (p[5] & 0x3E) >> 1
    section_number = p[6]
    last_section_number = p[7]
    network_descriptors_length = ((p[8] & 0x0F) << 8) | p[9]
    index = 10 + network_descriptors_length
    transport_stream_loop_length = ((p[index] & 0x0F) << 8) | p[index+1]

    base = {
        'table_id': table_id,
        'network_id': network_id,
        'version_number': version_number,
        'section_number': section_number,
        'last_section_number': last_section_number,
    }
    base.update(descriptors(p[10:10+network_descriptors_length]))
    start = index + 2
    end = section_length - 4
    while start < end:
        transport_stream_id = (p[start] << 8) | p[start+1]
        original_network_id = (p[start+2] << 8) | p[start+3]
        transport_descriptors_length = ((p[start+4] & 0x0F) << 8) | p[start+5]
        additional = {
            'transport_stream_id': transport_stream_id,
            'original_network_id': original_network_id,
        }
        additional.update(descriptors(
            p[start+6:start+6+transport_descriptors_length]))

        yield dict(base, **additional)
        start += 6 + transport_descriptors_length


def service_descriptions(p):
    """SDTのパースを行う"""

    table_id = p[0]
    section_length = ((p[1] & 0x0F) << 8) | p[2]
    transport_stream_id = (p[3] << 8) | p[4]
    version_number = (p[5] & 0x3E) >> 1
    section_number = p[6]
    last_section_number = p[7]
    original_network_id = (p[8] << 8) | p[9]

    base = {
        'table_id': table_id,
        'transport_stream_id': transport_stream_id,
        'version_number': version_number,
        'section_number': section_number,
        'last_section_number': last_section_number,
        'original_network_id': original_network_id,
    }
    start = 11
    end = section_length - 4
    while start < end:
        service_id = (p[start] << 8) | p[start+1]
        eit_user_defined_flags = (p[start+2] & 0x1C) >> 2
        eit_schedule_flag = (p[start+2] & 0x02) >> 1
        eit_present_following_flag = p[start+2] & 0x01
        running_status = (p[start+3] & 0xE0) >> 5
        free_ca_mode = (p[start+3] & 0x10) >> 4
        descriptors_loop_length = ((p[start+3] & 0x0f) << 8) | p[start+4]
        additional = {
            'service_id': service_id,
            'eit_user_defined_flags': eit_user_defined_flags,
            'eit_schedule_flag': eit_schedule_flag,
            'eit_present_following_flag': eit_present_following_flag,
            'running_status': running_status,
            'free_ca_mode': free_ca_mode,
        }
        additional.update(descriptors(
            p[start+5:start+5+descriptors_loop_length]))

        yield dict(base, **additional)
        start += 5 + descriptors_loop_length


def event_informations(p):
    """EITのパースを行う"""

    table_id = p[0]
    section_length = ((p[1] & 0x0F) << 8) | p[2]
    service_id = (p[3] << 8) | p[4]
    version_number = (p[5] & 0x3E) >> 1
    section_number = p[6]
    last_section_number = p[7]
    transport_stream_id = (p[8] << 8) | p[9]
    original_network_id = (p[10] << 8) | p[11]
    segment_last_section_number = p[12]
    last_table_id = p[13]

    base = {
        'table_id': table_id,
        'section_length': section_length,
        'service_id': service_id,
        'version_number': version_number,
        'section_number': section_number,
        'last_section_number': last_section_number,
        'transport_stream_id': transport_stream_id,
        'original_network_id': original_network_id,
        'segment_last_section_number': segment_last_section_number,
        'last_table_id': last_table_id,
    }
    start = 14
    end = section_length - 4
    while start < end:
        event_id = (p[start] << 8) | p[start+1]
        start_time = parse.mjd(p[start+2:start+7])
        duration = parse.bcdtime(p[start+7:start+10])
        running_status = (p[start+10] & 0xE0) >> 5
        free_ca_mode = (p[start+10] & 0x10) >> 4
        descriptors_loop_length = ((p[start+10] & 0x0f) << 8) | p[start+11]
        additional = {
            'event_id': event_id,
            'start_time': start_time,
            'duration': duration,
            'running_status': running_status,
            'free_ca_mode': free_ca_mode,
        }
        additional.update(descriptors(
            p[start+12:start+12+descriptors_loop_length]))

        yield dict(base, **additional)
        start += 12 + descriptors_loop_length
