from ariblib.descriptors import descriptors


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
