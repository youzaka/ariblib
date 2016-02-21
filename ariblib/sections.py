from ariblib import parse
from ariblib.caption import CProfileString
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


def canditional_accesses(p):
    """CATのパースを行う"""

    table_id = p[0]
    section_length = ((p[1] & 0x0F) << 8) | p[2]
    version_number = (p[5] & 0x3E) >> 1
    section_number = p[6]
    last_section_number = p[7]
    base = {
        'table_id': table_id,
        'section_length': section_length,
        'version_number': version_number,
        'section_number': section_number,
        'last_section_number': last_section_number,
    }
    base.update(descriptors(p[8:section_length-1]))
    yield base


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


def broadcaster_informations(p):
    """BITのパースを行う"""

    table_id = p[0]
    section_length = ((p[1] & 0x0F) << 8) | p[2]
    original_network_id = (p[3] << 8) | p[4]
    version_number = (p[5] & 0x3E) >> 1
    section_number = p[6]
    last_section_number = p[7]
    broadcast_view_priority = (p[8] & 0x10) >> 4
    first_descriptors_length = ((p[8] & 0x0F) << 8) | p[9]
    start = 10 + first_descriptors_length
    end = section_length - 4

    base = {
        'table_id': table_id,
        'original_network_id': original_network_id,
        'version_number': version_number,
        'section_number': section_number,
        'last_section_number': last_section_number,
    }
    base.update(descriptors(p[10:start]))

    while start < end:
        broadcaster_id = p[start]
        broadcaster_descriptor_length = ((p[start+1] & 0x0F) << 8) | p[start+2]
        additional = {
            'broadcaster_id': broadcaster_id,
        }
        start += 3
        stop = start + broadcaster_descriptor_length
        additional.update(descriptors(p[start:stop]))
        yield dict(base, **additional)
        start = stop


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


def time_offsets(p):
    """TOTのパースを行う"""

    table_id = p[0]
    section_length = ((p[1] & 0x0F) << 8) | p[2]
    jst_time = parse.mjd(p[3:8])
    descriptors_loop_length = ((p[8] & 0x0F) << 8) | p[9]
    base = {
        'table_id': table_id,
        'section_length': section_length,
        'jst_time': jst_time,
    }
    base.update(descriptors(p[10:10+descriptors_loop_length]))
    yield base


def common_data(p):
    """CDTのパースを行う"""

    table_id = p[0]
    section_length = ((p[1] & 0x0F) << 8) | p[2]
    download_data_id = (p[3] << 8) | p[4]
    version_number = (p[5] & 0x3E) >> 1
    section_number = p[6]
    last_section_number = p[7]
    original_network_id = (p[8] << 8) | p[9]
    data_type = p[10]
    descriptors_loop_length = ((p[11] & 0x0F) << 8) | p[12]
    index = 13 + descriptors_loop_length
    base = {
        'table_id': table_id,
        'section_length': section_length,
        'download_data_id': download_data_id,
        'version_number': version_number,
        'section_number': section_number,
        'last_section_number': last_section_number,
        'original_network_id': original_network_id,
        'data_type': data_type,
    }
    base.update(descriptors(p[13:index]))

    logo_type = p[index]
    logo_id = ((p[index+1] & 0x01) << 8) | p[index+2]
    logo_version = ((p[index+3] & 0x0F) << 8) | p[index+4]
    data_size = (p[index+5] << 8) | p[index+6]
    data_byte = p[index+7:index+7+data_size]
    additional = {
        'logo_type': logo_type,
        'logo_id': logo_id,
        'logo_version': logo_version,
        'data_byte': data_byte,
    }
    yield dict(base, **additional)


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


def captions(p):
    """字幕のパースを行う"""

    stream_id = p[3]
    pes_packet_length = (p[4] << 8) | p[5]
    pes_header_data_length = p[8]
    pts = (((p[9] & 0x0E) << 29) | (p[10] << 22) | ((p[11] & 0xFE) << 14) |
           (p[12] << 7) | ((p[13] & 0xFE) >> 1))
    delta = parse.pts(pts)
    index = pes_header_data_length + 9
    data_identifier = p[index]
    private_stream_id = p[index+1]
    pes_data_packet_header_length = p[index+2] & 0x0F
    index += 3 + pes_data_packet_header_length
    data_group_id = (p[index] & 0xFC) >> 2
    data_group_version = p[index] & 0x03
    data_group_link_number = p[index+1]
    last_data_group_link_number = p[index+2]
    data_group_size = (p[index+3] << 8) | p[index+4]

    index += 5
    if data_group_id in (0x0, 0x20):
        tmd = (p[index] & 0xC0) >> 6
        if tmd == 0b10:
            index += 5
        num_languages = p[index+1]
        index += 2
        for _ in range(num_languages):
            language_tag = (p[index] & 0xE0) >> 5
            dmf1 = (p[index] & 0x0C) >> 2
            dmf2 = p[index] & 0x03
            if dmf1 == 0b11:
                index += 1
            caption_lang = p[index+1:index+4].decode('UTF-8')
            format_ = (p[index+4] & 0xF0) >> 4
            tcs = (p[index+4] & 0x0C) >> 2
            rollup_mode = p[index+4] & 0x03
            index += 5
    else:
        tmd = (p[index] & 0xC0) >> 6
        if tmd in (0b01, 0b10):
            index += 5
        index += 1
    data_unit_loop_length = (p[index] << 16) | (p[index+1] << 8) | p[index+2]
    start = index + 3
    end = start + data_unit_loop_length
    while start < end:
        unit_separator = p[start]
        data_unit_parameter = p[start+1]
        data_unit_size = (p[start+2] << 16) | (p[start+3] << 8) | p[start+4]
        start += 5
        stop = start + data_unit_size
        if data_unit_parameter == 0x20:
            data_unit_data = p[start:stop]
            yield {
                'delta': delta,
                'body': str(CProfileString(data_unit_data)),
            }
            start = stop
        elif data_unit_parameter == 0x30:
            number_of_code = p[start]
            start += 1
            codes = []
            for _ in range(number_of_code):
                character_code = (p[start] << 8) | p[start+1]
                number_of_font = p[start+2]
                start += 3
                fonts = []
                for __ in range(number_of_font):
                    font_id = (p[start] & 0xF0) >> 4
                    mode = p[start] & 0x0F
                    depth = p[start+1]
                    width = p[start+2]
                    height = p[start+3]
                    start += 4
                    patterns = []
                    for ___ in range(height):
                        pattern_data = p[start:start+2]
                        patterns.append(pattern_data)
                        start += 2
                    fonts.append({
                        'font_id': font_id,
                        'mode': mode,
                        'depth': depth,
                        'width': width,
                        'height': height,
                        'patterns': patterns,
                    })
                codes.append({
                    'character_code': character_code,
                    'number_of_font': number_of_font,
                    'fonts': fonts,
                })
            yield {
                'codes': codes,
            }
