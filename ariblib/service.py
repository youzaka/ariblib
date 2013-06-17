#!/usr/bin/env python3.2

"""サービスラッパー"""

from ariblib.descriptors import *
from ariblib.sections import (ServiceDescriptionSection,
    ActualStreamServiceDescriptionSection,
    OtherStreamServiceDescriptionSection)

def services(ts, channel_id=None, stream=None):
    """トランスポートストリームから Service オブジェクトを返すジェネレータ"""

    if channel_id is None:
        get_channel_id = lambda service: service.service_id
    else:
        get_channel_id = lambda service: channel_id

    if stream == 'actual':
        SDT = ActualStreamServiceDescriptionSection
    elif stream == 'other':
        SDT = OtherStreamServiceDescriptionSection
    else:
        SDT = ServiceDescriptionSection

    for sdt in ts.sections(SDT):
        for service in sdt.services:
            yield Service(service, get_channel_id(service))


class Service(object):

    """サービスラッパークラス"""

    def __init__(self, service, channel_id):
        self.channel_id = channel_id
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

