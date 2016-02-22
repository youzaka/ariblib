from ariblib import parse
from ariblib.aribstr import AribString


_descriptors = {}


def descriptors(p):
    eeds = []
    while p:
        descriptor_tag = p[0]
        descriptor_length = p[1]
        start = 2
        end = start + descriptor_length
        descriptor = p[start:end]
        if descriptor_tag == 0x4E:
            eeds.append(_descriptors.get(descriptor_tag)(descriptor))
        else:
            yield from _descriptors.get(descriptor_tag)(descriptor).items()
        p = p[end:]

    if eeds:
        yield ('detail', list(extended_events(eeds)))


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


@tag(0x43)
def satellite_delivery_system_dscriptor(p):
    """衛星分配システム記述子(ARIB-STD-B10-2-6.2.6)"""

    frequency = parse.bcd(p[0:4], 6)
    orbital_position = parse.bcd(p[4:6], 1)
    west_east_flag = (p[6] & 0x80) >> 7
    polarisation = (p[6] & 0x60) >> 5
    modulation = p[6] & 0x1F
    # symbol_rate = o bcd(28, 5)
    fec_inner = p[10] & 0x0F
    return {
        'frequency': frequency,
        'orbital_position': orbital_position,
        'west_east_flag': west_east_flag,
        'polarisation': polarisation,
        'modulation': modulation,
        'fec_inner': fec_inner,
    }


@tag(0x48)
def service_descriptor(p):
    """サービス記述子(ARIB-STD-B10-2-6.2.13)"""

    service_type = p[0]
    service_provider_name_length = p[1]
    index = 2 + service_provider_name_length
    service_provider_name = str(AribString(p[2:index]))
    index += 1
    service_name_length = p[index]
    end = index + service_provider_name_length
    service_name = str(AribString(p[index:end]))
    return {
        'service_type': service_type,
        'service_provider_name': service_provider_name,
        'service_name': service_name,
    }


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


@tag(0x4D)
def short_event_descriptor(p):
    """短形式イベント記述子(ARIB-STD-B10-2-6.2.15)"""

    iso_639_language_code = p[0:3].decode('UTF-8')
    event_name_length = p[3]
    index = 4 + event_name_length
    event_name_char = str(AribString(p[4:index]))
    text_length = p[index]
    index += 1
    end = index + text_length
    text_char = str(AribString(p[index:end]))
    return {
        'text_lang': iso_639_language_code,
        'event_name_char': event_name_char,
        'text_char': text_char,
    }


@tag(0x4E)
def extended_event_descriptor(p):
    """拡張形式イベント記述子(ARIB-STD-B10-2-6.2.7)"""

    descriptor_number = (p[0] & 0xF0) >> 4
    last_descriptor_number = p[0] & 0x0F
    iso_639_language_code = p[1:4].decode('UTF-8')
    length_of_items = p[4]
    items = []

    start = 5
    end = 5 + length_of_items
    while start < end:
        item_description_length = p[start]
        start += 1
        stop = start + item_description_length
        item_description_char = str(AribString(p[start:stop]))
        start = stop
        item_length = p[start]
        start += 1
        stop = start + item_length
        item_char = p[start:stop]
        start = stop
        items.append({
            'item_description_char': item_description_char,
            'item_char': item_char,
        })

    text_length = p[start]
    start += 1
    stop = start + text_length
    text_char = str(AribString(p[start:stop]))
    return {
        'descriptor_number': descriptor_number,
        'last_descriptor_number': last_descriptor_number,
        'description_lang': iso_639_language_code,
        'items': items,
        'text_char': text_char,
    }


def extended_events(eeds):
    sections = []
    for eed in eeds:
        for item in eed['items']:
            title = item['item_description_char']
            body = item['item_char']
            lang = eed['description_lang']
            if not sections or title != '' or title == sections[-1]['title']:
                sections.append({
                    'title': title,
                    'body': bytearray(body),
                    'description_lang': lang,
                })
            else:
                sections[-1]['body'].extend(bytearray(body))
    for section in sections:
        section['body'] = str(AribString(section['body']))
        yield section


@tag(0x50)
def component_descriptor(p):
    """コンポーネント記述子(ARIB-STD-B10-2-6.2.3)"""

    stream_content = p[0] & 0x0F
    component_type = p[1]
    component_tag = p[2]
    iso_639_language_code = p[3:6].decode('UTF-8')
    component_text = str(AribString(p[6:]))
    return {
        'stream_content': stream_content,
        'component_type': component_type,
        'component_tag': component_tag,
        'component_lang': iso_639_language_code,
        'component_text': component_text,
    }


@tag(0x52)
def stream_identifier_descriptor(p):
    """ストリーム識別記述子 (ARIB-STD-B10-2-6.2.16)"""

    return {
        'component_tag': p[0],
    }


@tag(0x54)
def content_descriptor(p):
    """コンテント記述子(ARIB-STD-B10-2-6.2.4)"""

    nibbles = []
    while p:
        content_nibble_level_1 = (p[0] & 0xF0) >> 4
        content_nibble_level_2 = p[0] & 0x0F
        user_nibble_level_1 = (p[1] & 0xF0) >> 4
        user_nibble_level_2 = p[1] & 0x0F
        nibbles.append((
            content_nibble_level_1,
            content_nibble_level_2,
            user_nibble_level_1,
            user_nibble_level_2))
        p = p[2:]
    return {
        'nibbles': nibbles,
    }


@tag(0x55)
def parental_rating_descriptor(p):
    """パレンタルレート記述子(ARIB-STD-B10-2-6.2.12)"""

    ratings = []
    while p:
        country_code = p[0:3].decode('UTF-8')
        rating = p[3]
        ratings.append({
            'country_code': country_code,
            'rating': rating,
        })
        p = p[4:]
    return {'ratings': ratings}


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


@tag(0xC4)
def audio_component_descriptor(p):
    """音声コンポーネント記述子(ARIB-STD-B10-2-6.2.26)"""

    stream_content = p[0] & 0x0F
    component_type = p[1]
    component_tag = p[2]
    stream_type = p[3]
    simulcast_group_tag = p[4]
    es_multi_lingual_flag = (p[5] & 0x80) >> 7
    main_component_flag = (p[5] & 0x40) >> 6
    quality_indicator = (p[5] & 0x30) >> 4
    sampling_rate = (p[5] & 0x0E) >> 1
    iso_639_language_code = p[6:9].decode('UTF-8')
    index = 9

    if es_multi_lingual_flag:
        iso_639_language_code_2 = p[9:12].decode('UTF-8')
        index += 3
        audio_text = str(AribString(p[index:]))
        return {
            'stream_content': stream_content,
            'component_type': component_type,
            'component_tag': component_tag,
            'stream_type': stream_type,
            'simulcast_group_tag': simulcast_group_tag,
            'es_multi_lingual_flag': es_multi_lingual_flag,
            'main_component_flag': main_component_flag,
            'quality_indicator': quality_indicator,
            'sampling_rate': sampling_rate,
            'audio_lang': iso_639_language_code,
            'audio_lang_2': iso_639_language_code_2,
            'audio_text': audio_text,
        }

    audio_text = str(AribString(p[index:]))
    return {
        'stream_content': stream_content,
        'component_type': component_type,
        'component_tag': component_tag,
        'stream_type': stream_type,
        'simulcast_group_tag': simulcast_group_tag,
        'es_multi_lingual_flag': es_multi_lingual_flag,
        'main_component_flag': main_component_flag,
        'quality_indicator': quality_indicator,
        'sampling_rate': sampling_rate,
        'audio_lang': iso_639_language_code,
        'audio_text': audio_text,
    }


@tag(0xC7)
def data_content_descriptor(p):
    """データコンテンツ記述子(ARIB-STD-B10-2-6.2.28)

    data_component_idが0x0008のものは、selector_byteに
    字幕・文字スーパーの識別情報が入っている(ARIB-STD-B24-1-3-9.6.2)

    """

    data_component_id = (p[0] << 8) | p[1]
    entry_component = p[2]
    selector_length = p[3]
    base = {
        'data_component_id': data_component_id,
        'entry_component': entry_component,
    }

    # ARIB-STD-B24-1-3-9.6.2
    if data_component_id == 0x08:
        languages = []
        num_languages = p[4]
        index = 5
        for _ in range(num_languages):
            language_tag = (p[index] & 0xE0) >> 5
            dmf = p[index] & 0x0F
            iso_639_language_code = p[index+1:index+4].decode('UTF-8')
            languages.append({
                'language_tag': language_tag,
                'dmf': dmf,
                'caption_lang': iso_639_language_code,
            })
        base.update({'languages': languages})
    index = 4 + selector_length
    num_of_component_ref = p[index]
    component_refs = []
    index += 1
    for _ in range(num_of_component_ref):
        component_ref = p[index]
        component_refs.append(component_ref)
        index += 1

    iso_639_language_code = p[index:index+3].decode('UTF-8')
    text_length = p[index+3]
    index += 4
    end = index + text_length
    data_text = str(AribString(p[index:end]))
    base.update({
        'component_refs': component_refs,
        'data_lang': iso_639_language_code,
        'data_text': data_text,
    })
    return base


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


@tag(0xCE)
def extended_broadcaster_descriptor(p):
    """拡張ブロードキャスタ記述子(ARIB-STD-B10-2-6.2.43)"""

    broadcaster_type = (p[0] & 0xF0) >> 4

    if broadcaster_type == 0x1:
        terrestrial_broadcaster_id = (p[1] << 8) | p[2]
        number_of_affiliation_id_loop = (p[3] & 0xF0) >> 4
        number_of_broadcaster_id_loop = p[3] & 0x0F
        affiliations = []
        broadcasters = []
        index = 4
        for _ in range(number_of_affiliation_id_loop):
            affiliation_id = p[index]
            affiliations.append(affiliation_id)
            index += 1
        for _ in range(number_of_broadcaster_id_loop):
            original_network_id = p[index]
            broadcaster_id = p[index+1]
            broadcasters.append({
                'original_network_id': original_network_id,
                'broadcaster_id': broadcaster_id,
            })
            index += 2
        return {
            'broadcaster_type': broadcaster_type,
            'terrestrial_broadcaster_id': terrestrial_broadcaster_id,
            'affiliations': affiliations,
            'broadcasters': broadcasters,
        }
    if broadcaster_type == 0x2:
        terrestrial_sound_broadcaster_id = (p[1] << 8) | p[2]
        number_of_sound_broadcast_affiliation_id_loop = (p[3] & 0xF0) >> 4
        number_of_broadcaster_id_loop = p[3] & 0x0F
        sound_broadcast_affiliations = []
        broadcasters = []
        index = 4
        for _ in range(number_of_sound_broadcast_affiliation_id_loop):
            sound_broadcast_affiliations_id = p[index]
            sound_broadcast_affiliations.append(
                sound_broadcast_affiliations_id)
            index += 1
        for _ in range(number_of_broadcaster_id_loop):
            original_network_id = p[index]
            broadcaster_id = p[index+1]
            broadcasters.append({
                'original_network_id': original_network_id,
                'broadcaster_id': broadcaster_id,
            })
            index += 2
        return {
            'broadcaster_type': broadcaster_type,
            'terrestrial_sound_broadcaster_id':
                terrestrial_sound_broadcaster_id,
            'sound_broadcast_affiliations': sound_broadcast_affiliations,
            'broadcasters': broadcasters,
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


@tag(0xD6)
def event_group_descriptor(p):
    """イベントグループ記述子 (ARIB-STD-B10-2-6.2.34)"""

    group_type = (p[0] & 0xF0) >> 4
    event_count = p[0] & 0x0F
    events = []

    index = 1
    for _ in range(event_count):
        service_id = (p[index] << 8) | p[index+1]
        event_id = (p[index+2] << 8) | p[index+3]
        events.append({
            'service_id': service_id,
            'event_id': event_id,
        })
        index += 4

    if group_type in (4, 5):
        networks = []
        for _ in range(event_count):
            original_network_id = (p[index] << 8) | p[index+1]
            transport_stream_id = (p[index+2] << 8) | p[index+3]
            service_id = (p[index+4] << 8) | p[index+5]
            event_id = (p[index+6] << 8) | p[index+7]
            networks.append({
                'original_network_id': original_network_id,
                'transport_stream_id': transport_stream_id,
                'service_id': service_id,
                'event_id': event_id,
            })
            index += 8
        return {
            'group_type': group_type,
            'event_count': event_count,
            'events': events,
            'networks': networks,
        }
    return {
        'group_type': group_type,
        'event_count': event_count,
        'events': events,
    }


@tag(0xD7)
def si_parameter_descriptor(p):
    """SI伝送パラメータ記述子(ARIB-STD-B10-2-6.2.35)"""

    parameter_version = p[0]
    update_time = parse.mjd(p[1:3])
    parameters = []

    p = p[3:]
    while p:
        table_id = p[0]
        table_description_length = p[1]

        # ARIB-TR-B14-31.1.2.1, ARIB-TR-B15-31.2.2.1
        if (table_id in (0x40, 0x42, 0x46, 0x4E, 0x4F, 0xC4) and
                table_description_length == 1):
            table_cycle = parse.bcd(p[2:3])
            parameters.append({
                'table_id': table_id,
                'table_cycle': table_cycle,
            })
            p = p[3:]
        elif table_id in (0xC3, 0xC8):
            table_cycle = parse.bcd(p[2:4])
            parameters.append({
                'table_id': table_id,
                'table_cycle': table_cycle,
            })
            p = p[4:]
        elif table_id == 0x4E and table_description_length == 4:
            table_cycle_H_EIT_PF = parse.bcd(p[2:3])
            table_cycle_M_EIT = parse.bcd(p[3:4])
            table_cycle_L_EIT = parse.bcd(p[4:5])
            num_of_M_EIT_event = (p[5] & 0xF0) >> 4
            num_of_L_EIT_event = p[5] & 0x0F
            parameters.append({
                'table_id': table_id,
                'parameter_version': parameter_version,
                'update_time': update_time,
                'table_cycle_H_EIT_PF': table_cycle_H_EIT_PF,
                'table_cycle_M_EIT': table_cycle_M_EIT,
                'table_cycle_L_EIT': table_cycle_L_EIT,
                'num_of_M_EIT_event': num_of_M_EIT_event,
                'num_of_L_EIT_event': num_of_L_EIT_event,
            })
            p = p[6:]
        elif table_id in (0x50, 0x58, 0x60):
            cycles = []
            start = 2
            end = start + table_description_length
            while start < end:
                media_type = (p[start] & 0xC0) >> 6
                pattern = (p[start] & 0x30) >> 4
                schdule_range = parse.bcd(p[start+1:start+2])
                # base_cycle = bcd(12)
                cycle_group_count = p[start+4] & 0x0F
                groups = []
                start = 5
                for _ in range(cycle_group_count):
                    num_of_segment = parse.bcd(p[start:start+1])
                    cycle = parse.bcd(p[start+1:start+2])
                    groups.append({
                        'num_of_segment': num_of_segment,
                        'cycle': cycle,
                    })
                    start += 2
                cycles.append({
                    'media_type': media_type,
                    'pattern': pattern,
                    'schdule_range': schdule_range,
                    'groups': groups,
                })
            parameters.append({
                'table_id': table_id,
                'parameter_version': parameter_version,
                'update_time': update_time,
                'cycles': cycles,
            })
            p = p[end:]
    return {
        'parameter_version': parameter_version,
        'update_time': update_time,
        'parameters': parameters,
    }


@tag(0xDC)
def ldt_linkage_descriptor(p):
    """LDTリンク記述子(ARIB-STD-B10-2.6.2.40)"""

    original_service_id = (p[0] << 8) | p[1]
    transport_stream_id = (p[2] << 8) | p[3]
    original_network_id = (p[4] << 8) | p[5]
    descriptors = []

    p = p[6:]
    while p:
        description_id = (p[0] << 8) | p[1]
        description_type = p[2] & 0x0F
        user_defined = p[3]
        descriptors.append({
            'description_id': description_id,
            'description_type': description_type,
            'user_defined': user_defined,
        })
        p = p[4:]
    return {
        'ldt_original_service_id': original_service_id,
        'ldt_transport_stream_id': transport_stream_id,
        'ldt_original_network_id': original_network_id,
        'ldt_descriptors': descriptors,
    }


@tag(0xDE)
def content_availability_descriptor(p):
    """コンテント利用記述子 (ARIB-STD-B10-2-6.2.45)"""

    copy_restriction_mode = (p[0] & 0x40) >> 6
    image_constraint_token = (p[0] & 0x20) >> 5
    retention_mode = (p[0] & 0x10) >> 4
    retention_state = (p[0] & 0x0E) >> 1
    encryption_mode = p[0] & 0x01
    return {
        'copy_restriction_mode': copy_restriction_mode,
        'image_constraint_token': image_constraint_token,
        'retention_mode': retention_mode,
        'retention_state': retention_state,
        'encryption_mode': encryption_mode,
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
