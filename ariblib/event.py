#!/usr/bin/env python3.2

"""イベントラッパー"""

from ariblib.aribstr import AribString
from ariblib.constants import *
from ariblib.descriptors import *
from ariblib.sections import EventInformationSection

def events(ts):
    """トランスポートストリームから Event オブジェクトを返すジェネレータ"""

    for eit in ts.sections(EventInformationSection):
        for event in eit.events:
            yield Event(eit, event)

class Event(object):

    """イベントラッパークラス"""

    from_eit = ['service_id', 'transport_stream_id', 'original_network_id']
    from_event = ['event_id', 'start_time', 'duration']

    def __init__(self, eit, event):
        for field in self.from_eit:
            setattr(self, field, getattr(eit, field))
        for field in self.from_event:
            setattr(self, field, getattr(event, field))

        desc = event.descriptors
        for sed in desc.get(ShortEventDescriptor, []):
            self.title = sed.event_name_char
            self.desc = sed.text_char
        for cd in desc.get(ComponentDescriptor, []):
            self.video_stream_content = cd.stream_content
            self.video_component_type = cd.component_type
            self.video = COMPONENT_TYPE[cd.stream_content][cd.component_type]
            self.component_text = cd.component_text
        for dccd in desc.get(DigitalCopyControlDescriptor, []):
            self.copy_control_type = dccd.copy_control_type
            self.copy = DIGITAL_RECORDING_CONTROL_TYPE[dccd.copy_control_type]
        for acd in desc.get(AudioComponentDescriptor, []):
            if acd.main_component_flag:
                self.audio_stream_content = acd.stream_content
                self.audio_component_type = acd.component_type
                self.samplint_rate_type = acd.sampling_rate
                self.audio = COMPONENT_TYPE[acd.stream_content][acd.component_type]
                self.sampling_rate = acd.sampling_rate
                self.sampling_rate_string = SAMPLING_RATE[acd.sampling_rate]
                self.audio_text = acd.audio_text
            else:
                self.second_audio_stream_content = acd.stream_content
                self.second_audio_component_type = acd.component_type
                self.second_audio = COMPONENT_TYPE[acd.stream_content][acd.component_type]
                self.second_sampling_rate = acd.sampling_rate
                self.second_sampling_rate_string = SAMPLING_RATE[acd.sampling_rate]
                self.second_audio_text = acd.audio_text
        for egd in desc.get(EventGroupDescriptor, []):
            self.group_type = egd.group_type
            self.group_type_string = EVENT_GROUP_TYPE[egd.group_type]
            self.events = dict((e.service_id, e.event_id) for e in egd.events)
        for ctd in desc.get(ContentDescriptor, []):
            nibble = ctd.nibbles[0]
            self.nibble1 = nibble.content_nibble_level_1
            self.nibble2 = nibble.content_nibble_level_2
            self.genre = CONTENT_TYPE[nibble.content_nibble_level_1][0]
            self.subgenre = (CONTENT_TYPE[nibble.content_nibble_level_1][1]
                                         [nibble.content_nibble_level_2])
        detail = [('', [])]
        for eed in desc.get(ExtendedEventDescriptor, []):
            for item in eed.items:
                key = item.item_description_char
                # タイトルが空か一つ前と同じ場合は本文を一つ前のものにつなげる
                if str(key) == '' or str(detail[-1][0]) == str(key):
                    detail[-1][1].extend(item.item_char)
                else:
                    detail.append((key, item.item_char))
        detail = [(key, AribString(value)) for key, value in detail[1:]]
        self.detail = dict(detail)
        self.longdesc = '\n'.join("{}\n{}\n".format(key, value) for key, value in detail)


