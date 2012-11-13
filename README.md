ariblib
=======

速度優先の Transport Stream パーサです。
Python 3.2 での動作が前提ですが、3.1 でも動くかもしれません。

```
$ sudo python3.2 setup.py install
```

ARIB-STD で定義されているデータ構造をなるべく近い形で
Python コードとして記述できるようにしています。

たとえば、 Program Map Section のデータ構造は ARIB-STD-B10 第2部付録E 表E-3 で
以下のように記述されています:

```
TS_program_map_section(){
    table_id                   8  uimsbf
    section_syntax_indicator   1  bslbf
    ‘0’                        1  bslbf
    reserved                   2  bslbf
    section_length            12  uimsbf
    program_number            16  uimsbf
    reserved                   2  bslbf
    version_number             5  uimsbf
    current_next_indicator     1  bslbf
    section_number             8  uimsbf
    last_section_number        8  uimsbf
    reserved                   3  bslbf
    PCR_PID                   13  uimsbf
    reserved                   4  bslbf
    program_info_length       12  uimsbf
    for (i=0;i<N;i++){
        descriptor()
    }
    for (i=0;i<N1;i++){
        stream_type            8  uimsbf
        reserved               3  bslbf
        elementary_PID        13  uimsbf
        reserved               4  bslbf
        ES_info_length        12  uimsbf
        for (i=0;i<N2;i++){
            descriptor()
        }
    }
    CRC_32                    32 rpchof
```
これを ariblib では以下のように記述します。 (説明に必要でない行は省略しています)
```python

class ProgramMapSection(Section):
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

    @loop(lambda self: self.section_length - (13 + self.program_info_length))
    class maps(Syntax):
        stream_type = uimsbf(8)
        reserved_1 = bslbf(3)
        elementary_PID = uimsbf(13)
        reserved_2 = bslbf(4)
        ES_info_length = uimsbf(12)
        descriptors = descriptors(ES_info_length)

    CRC_32 = rpchof(32)
```

ビット列表記をディスクリプタとして実装したり、繰り返し構造や制御構造をデコレータとして実装したり
することで、なるべく仕様書に近い形でクラスの表記ができるようにしてます。

使い方例1 字幕を表示
```python

from ariblib import tsopen
from ariblib.caption import captions

import sys

with tsopen(sys.argv[1]) as ts:
    for caption in captions(ts, color=True):
        body = str(caption.body)

        # アダプテーションフィールドの PCR の値と、そこから一番近い TOT テーブルの値から、
        # 字幕の表示された時刻を計算します (若干誤差が出ます)
        # PCR が一周した場合の処理は実装されていません
        datetime = caption.datetime.strftime('%Y-%m-%d %H:%M:%S')
        print('\033[35m' + datetime + '\33[37m')
        print(body)
```

使い方例2 いま放送中の番組と次の番組を表示
```python

import sys

from ariblib import TransportStreamFile
from ariblib.descriptors import ShortEventDescriptor
from ariblib.sections import EventInformationSection

def show_program(eit):
    event = eit.events.__next__()
    program_title = event.descriptors[ShortEventDescriptor][0].event_name_char
    start = event.start_time
    return "{} {}".format(program_title, start)

with TransportStreamFile(sys.argv[1]) as ts:
    # 自ストリームの現在と次の番組を表示する
    EventInformationSection._table_ids = [0x4E]
    current = next(table for table in ts.sections(EventInformationSection)
                   if table.section_number == 0)
    following = next(table for table in ts.sections(EventInformationSection)
                     if table.section_number == 1)
    print('今の番組', show_program(current))
    print('次の番組', show_program(following))
```

使い方例3: 放送局名の一欄を表示
(地上波ではその局, BSでは全局が表示される)
```python

import sys

from ariblib import TransportStreamFile
from ariblib.constant import SERVICE_TYPES
from ariblib.descriptors import ServiceDescriptor
from ariblib.sections import ServiceDescriptionSection

with TransportStreamFile(sys.argv[1]) as ts:
    for sdt in ts.sections(ServiceDescriptionSection):
        for service in sdt.services:
            for sd in service.descriptors[ServiceDescriptor]:
                print(service.service_id, SERVICE_TYPE[sd.service_type],
                      sd.service_provider_name, sd.service_name)
```

使い方例4: 動画パケットの PID とその動画の解像度を表示
```python

import sys

from ariblib import TransportStreamFile
from ariblib.constants import VIDEO_ENCODE_FORMATS
from ariblib.descriptors import VideoDecodeControlDescriptor
from ariblib.sections import ProgramAssociationSection, ProgramMapSection

with TransportStreamFile(sys.argv[1]) as ts:
    pat = next(ts.sections(ProgramAssociationSection))
    ProgramMapSection._pids = list(pat.pmt_pids)
    for pmt in ts.sections(ProgramMapSection):
        for tsmap in pmt.maps:
            for vd in tsmap.descriptors.get(VideoDecodeControlDescriptor, []):
                print(tsmap.elementary_PID, VIDEO_ENCODE_FORMAT[vd.video_encode_format])
```

使い方例5: EPG情報の表示
```python
from ariblib import tsopen
from ariblib.event import events

import sys

with tsopen(sys.argv[1]) as ts:
    for event in events(ts):
        max_len = max(map(len, event.__dict__.keys()))
        template = "{:%ds}  {}" % max_len
        for key, value in event.__dict__.items():
            print(template.format(key, value))
        print('-' * 80)

```

使い方例6: 深夜アニメの出力
```python

import sys

from ariblib import TransportStreamFile
from ariblib.descriptors import ContentDescriptor, ShortEventDescriptor
from ariblib.sections import EventInformationSection

with TransportStreamFile(sys.argv[1]) as ts:
    EventInformationSection._table_ids = range(0x50, 0x70)
    for eit in ts.sections(EventInformationSection):
        for event in eit.events:
            for genre in event.descriptors.get(ContentDescriptor, []):
                nibble = next(genre.nibbles)
                if nibble.content_nibble_level_1 == 0x07 and not (4 < event.start_time.hour < 22):
                    for sed in event.descriptors.get(ShortEventDescriptor, []):
                        print(eit.service_id, event.event_id, event.start_time,
                              event.duration, sed.event_name_char, sed.text_char)
```

