"""サービスラッパー"""

from ariblib.descriptors import (
    LogoTransmissionDescriptor,
    ServiceDescriptor,
)
from ariblib.sections import (
    ActualStreamServiceDescriptionSection,
    OtherStreamServiceDescriptionSection,
    ServiceDescriptionSection,
)


def services(ts, channel_id=None, single=False, stream=None):
    """トランスポートストリームから Service オブジェクトを返すジェネレータ"""

    if channel_id is None:
        get_channel_id = lambda sdt: tsid2channel(sdt.transport_stream_id)
    else:
        get_channel_id = lambda sdt: str(channel_id)

    if stream == 'actual':
        SDT = ActualStreamServiceDescriptionSection
    elif stream == 'other':
        SDT = OtherStreamServiceDescriptionSection
    else:
        SDT = ServiceDescriptionSection

    if single:
        sdt = next(ts.sections(SDT))
        for service in sdt.services:
            yield Service(service, get_channel_id(sdt))
    else:
        for sdt in ts.sections(SDT):
            for service in sdt.services:
                yield Service(service, get_channel_id(sdt))


def parse_tsid(tsid):
    # NHK-BS対応
    if 16625 <= tsid <= 16626:
        tsid -= 1
    network_lower_4bit = (tsid & 0xF000) >> 12
    new = (tsid & 0x0E000) >> 9
    repeater = (tsid & 0x01F0) >> 4
    slot = tsid & 0x0007

    return (network_lower_4bit, new, repeater, slot)


def tsid2channel(tsid):
    """transport_stream_id を recpt1 が認識する channel 形式に変える"""
    lower, new, repeater, slot = parse_tsid(tsid)
    # ほんとはSystemManagementDescriptorのbroadcasting_identifierで
    # BS/CSの判別をすべきだと思う
    if repeater % 2 == 0:
        return "CS{:02d}".format(repeater)
    else:
        return "BS{:02d}_{}".format(repeater, slot)


class Service(object):

    """サービスラッパークラス"""

    def __init__(self, service, channel_id):
        self.channel_id = channel_id
        if 'BS' in channel_id:
            self.broadcasting_type = 'BS'
            self.channel_number =\
                int(channel_id.split('_')[0].replace('BS', ''))
        elif 'CS' in channel_id:
            self.broadcasting_type = 'CS'
            self.channel_number = int(channel_id.replace('CS', ''))
        else:
            self.broadcasting_type = 'GR'
            self.channel_number = int(channel_id)
        self.service_id = service.service_id
        self.eit_flags = service.EIT_user_defined_flags
        self.eit_schedule = service.EIT_schedule_flag
        self.pseit = service.EIT_present_following_flag
        descs = service.descriptors
        sd = descs[ServiceDescriptor][0]
        self.service_type = sd.service_type
        self.provider = sd.service_provider_name
        self.name = sd.service_name
        self.free_CA_mode = service.free_CA_mode
        self.logo = ''
        for ltd in descs[LogoTransmissionDescriptor]:
            if ltd.logo_transmission_type == 3:
                self.logo = ltd.logo_char
                break
