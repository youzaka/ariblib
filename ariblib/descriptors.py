from ariblib import parse
from ariblib.aribstr import AribString


_descriptors = {}


def descriptors(p):
    while p:
        descriptor_tag = p[0]
        descriptor_length = p[1]
        start = 2
        end = start + descriptor_length
        descriptor = p[start:end]
        yield from _descriptors.get(descriptor_tag)(descriptor).items()
        p = p[end:]


def tag(tag_id):
    def wrapper(func):
        _descriptors[tag_id] = func
        return func
    return wrapper


@tag(0x09)
def conditional_access_descriptor(p):
    """限定受信方式記述子 (ARIB-TR-B14-4-3.2.2.1, ARIB-TR-B15-4-3.2.2.1)"""

    ca_system_id = p[0]
    ca_pid = ((p[1] & 0x1F) < 8) | p[2]
    return {
        'ca_system_id': ca_system_id,
        'ca_pid': ca_pid,
    }


@tag(0x40)
def network_name_descriptor(p):
    """ネットワーク名記述子(ARIB-STD-B10-2.6.2.11)"""

    char = str(AribString(p))
    return {
        'network_name': char,
    }


@tag(0x41)
def service_list_descriptor(p):
    """サービスリスト記述子(ARIB-STD-B10-2-6.2.14)"""

    service_list = []
    while p:
        service_id = (p[0] << 8) | p[1]
        service_type = p[2]
        service_list.append({
            'service_id': service_id,
            'service_type': service_type,
        })
        p = p[3:]
    return {'service_list': service_list}


@tag(0x48)
def service_descriptor(p):
    """サービス記述子(ARIB-STD-B10-2-6.2.13)"""

    service_type = p[0]
    service_provider_name_length = p[1]
    index = 2 + service_provider_name_length
    service_provider_name = str(AribString(p[2:index]))
    service_name_length = p[index]
    index += 1
    end = index + service_name_length + 1
    service_name = str(AribString(p[index:end]))
    return {
        'service_type': service_type,
        'service_provider_name': service_provider_name,
        'service_name': service_name,
    }


@tag(0x4A)
def linkage_descriptor(p):
    """リンク記述子(ARIB-STD-B10-2.6.2.8)"""

    transport_stream_id = (p[0] << 8) | p[1]
    original_network_id = (p[2] << 8) | p[3]
    service_id = (p[4] << 8) | p[5]
    linkage_type = p[6]
    base = {
        'transport_stream_id': transport_stream_id,
        'original_network_id': original_network_id,
        'service_id': service_id,
        'linkage_type': linkage_type,
    }

    if linkage_type == 0x03:
        message_id = p[7]
        message = str(AribString(p[8:]))
        base.update({
            'message_id': message_id,
            'message': message,
        })
    return base


@tag(0x52)
def stream_identifier_descriptor(p):
    """ストリーム識別記述子 (ARIB-STD-B10-2-6.2.16)"""

    return {
        'component_tag': p[0],
    }


@tag(0xC1)
def digital_copy_control_descriptor(p):
    """デジタルコピー制御記述子 (ARIB-STD-B10-2-6.2.23)"""

    digital_recording_control_data = (p[0] & 0xC0) >> 6
    maximum_bitrate_flag = (p[0] & 0x20) >> 5
    component_control_flag = (p[0] & 0x10) >> 4
    copy_control_type = (p[0] & 0x0C) >> 2
    aps_control_data = p[0] & 0x03
    return {
        'digital_recording_control_data': digital_recording_control_data,
        'aps_control_data': aps_control_data,
    }


@tag(0xC8)
def video_decode_control_descriptor(p):
    """ビデオデコードコントロール記述子 (ARIB-STD-B10-2-6.2.30)"""

    still_picture_flag = (p[0] & 0x80) >> 7
    sequence_end_code_flag = (p[0] & 0x40) >> 6
    video_encode_format = (p[0] & 0x3C) >> 2

    return {
        'still_picture_flag': still_picture_flag,
        'sequence_end_code_flag': sequence_end_code_flag,
        'video_encode_format': video_encode_format,
    }


@tag(0xCB)
def encrypt_descriptor(p):
    """Encrypt記述子(ARIB-STD-B25-3.4.4.7)"""

    encrypt_id = p[0]
    return {
        'encrypt_id': encrypt_id,
    }


@tag(0xCD)
def ts_information_descriptor(p):
    """TS情報記述子(ARIB-STD-B10-2.6.2.42)"""

    remote_control_key_id = p[0]
    length_of_ts_name = (p[1] & 0xC0) >> 2
    transmission_type_count = p[1] & 0x03
    index = 2 + length_of_ts_name
    ts_name_char = str(AribString(p[2:index]))
    transmissions = []

    for _ in range(transmission_type_count):
        transmission_type_info = p[index]
        num_of_service = p[index+1]
        service_list = []
        index += 2
        for __ in range(num_of_service):
            service_id = (p[index] << 8) | p[index+1]
            service_list.append(service_id)
            index += 2

        transmissions.append({
            'transmission_type_info': transmission_type_info,
            'service_list': service_list,
        })
    return {
        'remote_control_key_id': remote_control_key_id,
        'ts_name_char': ts_name_char,
        'transmissions': transmissions,
    }


@tag(0xCF)
def logo_transmission_descriptor(p):
    """ロゴ伝送記述子(ARIB-STD-B10-2-6.2.44)"""

    logo_transmission_type = p[0]

    if logo_transmission_type == 0x01:
        logo_id = ((p[1] & 0x01) << 8) | p[2]
        logo_version = ((p[3] & 0x0F) << 8) | p[4]
        download_data_id = (p[5] < 8) | p[6]
        return {
            'logo_transmission_type': logo_transmission_type,
            'logo_id': logo_id,
            'logo_version': logo_version,
            'download_data_id': download_data_id,
        }
    elif logo_transmission_type == 0x02:
        logo_id = ((p[1] & 0x01) << 8) | p[2]
        return {
            'logo_transmission_type': logo_transmission_type,
            'logo_id': logo_id,
        }
    elif logo_transmission_type == 0x03:
        logo_char = str(AribString(p[1:]))
        return {
            'logo_transmission_type': logo_transmission_type,
            'logo_char': logo_char,
        }


@tag(0xF6)
def access_control_descriptor(p):
    """アクセス制御記述子 (ARIB-TR-B14 第四篇改定案 30.2.2.2)"""

    ca_system_id = (p[0] << 8) | p[1]
    transmission_type = (p[2] & 0xE0) >> 5
    pid = ((p[2] & 0x1F) << 8) | p[3]

    return {
        'access_ca_system_id': ca_system_id,
        'transmission_type': transmission_type,
        'access_ca_pid': pid,
    }


@tag(0xFA)
def terrestrial_delivery_system_descriptor(p):
    """地上分配システム記述子(ARIB-STD-B10-2-6.2.31)"""

    area_code = (p[0] << 4) | ((p[1] & 0xF0) >> 4)
    guard_interval = (p[1] & 0x0C) >> 2
    transmission_mode = p[1] & 0x03
    frequencies = [(q << 8) | r for q, r in zip(p[2::2], p[3::2])]
    return {
        'area_code': area_code,
        'guard_interval': guard_interval,
        'transmission_mode': transmission_mode,
        'frequencies': frequencies,
    }


@tag(0xFB)
def partial_reception_descriptor(p):
    """部分受信記述子(ARIB-STD-B10-2.6.2.32)"""

    service_list = []
    while p:
        service_id = (p[0] << 8) | p[1]
        service_list.append(service_id)
        p = p[2:]
    return {'partial_reception': service_list}


@tag(0xFD)
def data_component_descriptor(p):
    """データ符号化方式記述子(ARIB-STD-B10-2-6.2.20)

    data_component_idが0x0008のものは、additional_data_component_infoに
    字幕・文字スーパーの識別情報が入っている(ARIB-STD-B24-1-3-9.6.1)

    """

    data_component_id = (p[0] << 8) | p[1]

    if data_component_id == 0x08:
        dmf = (p[2] & 0xF0) >> 4
        timing = p[2] & 0x03
        return {
            'data_component_id': data_component_id,
            'dmf': dmf,
            'timing': timing,
        }
    elif data_component_id == 0x0C:
        transmission_format = (p[2] & 0xC0) >> 6
        entry_point_flag = (p[2] & 0x20) >> 5
        if entry_point_flag:
            auto_start_flag = (p[2] & 0x10) >> 4
            document_resolution = p[2] & 0x0F
            use_xml = (p[3] & 0x80) >> 7
            default_version_flag = (p[3] & 0x40) >> 6
            independent_flag = (p[3] & 0x20) >> 5
            style_for_tv_flag = (p[3] & 0x10) >> 4
            if default_version_flag == 0:
                bml_major_version = (p[4] << 8) | p[5]
                bml_minor_version = (p[6] << 8) | p[7]
                if use_xml == 1:
                    bxml_major_version = (p[8] << 8) | p[9]
                    bxml_minor_version = (p[10] << 8) | p[11]
                return {
                    'bml_major_version': bml_major_version,
                    'bml_minor_version': bml_minor_version,
                }
        else:
            data_event_id = (p[3] & 0xF0) >> 4
            event_section_flag = (p[3] & 0x08) >> 3
            ondemand_retrieval_flag = (p[4] & 0x80) >> 7
            file_storable_flag = (p[4] & 0x40) >> 6
            start_priority = (p[4] & 0x20) >> 5
            return {
                'data_event_id': data_event_id,
                'event_section_flag': event_section_flag,
                'ondemand_retrieval_flag': ondemand_retrieval_flag,
                'file_storable_flag': file_storable_flag,
                'start_priority': start_priority,
            }
    else:
        additional_data_component_info = p[1:]
        return {
            'data_component_id': data_component_id,
            'additional_data_component_info': additional_data_component_info,
        }


@tag(0xFE)
def system_management_descriptor(p):
    """システム管理記述子(ARIB-STD-B10-2-6.2.21, ARIB-TR-B14-30.4.2.2)"""

    broadcasting_flag = (p[0] & 0xC0) >> 6
    broadcasting_identifier = p[0] & 0x3F
    additional_broadcasting_identification = p[1]

    return {
        'broadcasting_flag': broadcasting_flag,
        'broadcasting_identifier': broadcasting_identifier,
        'additional_broadcasting_identification':
            additional_broadcasting_identification,
    }
