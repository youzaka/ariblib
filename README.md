# ariblib

ARIB-STD-B10 や ARIB-STD-B24 などの Python3+ での実装です。

m2tsをパースするライブラリと、応用を行ういくつかのコマンドからなります。

## インストール
pipからインストールするには以下のようにします:
```
$ sudo pip install ariblib
```

パッケージインストールがうまくいかない場合や、直接ソースコードからパッケージを作成する場合は:
```
$ git clone https://github.com/youzaka/ariblib.git
$ sudo python setup.py install
```

## コマンド利用例
### WebVTT 互換の字幕ファイルを作成する
```
$ python -m ariblib vtt SRC DST
```
とすると、 SRC にある ts ファイルを読みこみ、 DST に出力します。

- DST に `-` を指定すると標準出力に書き出します。

### tsから必要なストリームのみを取り出す(ワンセグなどの削除)
```
$ python -m ariblib split SRC DST
```
とすると、 SRC にある ts ファイルが指定する PAT 情報を読み込み、最初のストリームの動画・音声のみを保存した TS ファイルを DST に保存します。 TSSplitter のようなことができます。

## ライブラリ利用例
コマンド化されていないことも、直接ライブラリを使って操作すると実現できます。 (PullRequestは随時受け付けています)

### 例1: 字幕を表示
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

### 例2: いま放送中の番組と次の番組を表示
```python

import sys

from ariblib import tsopen
from ariblib.descriptors import ShortEventDescriptor
from ariblib.sections import EventInformationSection

def show_program(eit):
    event = eit.events.__next__()
    program_title = event.descriptors[ShortEventDescriptor][0].event_name_char
    start = event.start_time
    return "{} {}".format(program_title, start)

with tsopen(sys.argv[1]) as ts:
    # 自ストリームの現在と次の番組を表示する
    EventInformationSection._table_ids = [0x4E]
    current = next(table for table in ts.sections(EventInformationSection)
                   if table.section_number == 0)
    following = next(table for table in ts.sections(EventInformationSection)
                     if table.section_number == 1)
    print('今の番組', show_program(current))
    print('次の番組', show_program(following))
```

### 例3: 放送局名の一欄を表示
(地上波ではその局, BSでは全局が表示される)
```python

import sys

from ariblib import tsopen
from ariblib.constant import SERVICE_TYPES
from ariblib.descriptors import ServiceDescriptor
from ariblib.sections import ServiceDescriptionSection

with tsopen(sys.argv[1]) as ts:
    for sdt in ts.sections(ServiceDescriptionSection):
        for service in sdt.services:
            for sd in service.descriptors[ServiceDescriptor]:
                print(service.service_id, SERVICE_TYPE[sd.service_type],
                      sd.service_provider_name, sd.service_name)
```

### 例4: 動画パケットの PID とその動画の解像度を表示
```python

import sys

from ariblib import tsopen
from ariblib.constants import VIDEO_ENCODE_FORMATS
from ariblib.descriptors import VideoDecodeControlDescriptor
from ariblib.sections import ProgramAssociationSection, ProgramMapSection

with tsopen(sys.argv[1]) as ts:
    pat = next(ts.sections(ProgramAssociationSection))
    ProgramMapSection._pids = list(pat.pmt_pids)
    for pmt in ts.sections(ProgramMapSection):
        for tsmap in pmt.maps:
            for vd in tsmap.descriptors.get(VideoDecodeControlDescriptor, []):
                print(tsmap.elementary_PID, VIDEO_ENCODE_FORMAT[vd.video_encode_format])
```

### 例5: EPG情報の表示
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

### 例6: 深夜アニメの出力
```python

import sys

from ariblib import tsopen
from ariblib.descriptors import ContentDescriptor, ShortEventDescriptor
from ariblib.sections import EventInformationSection

with tsopen(sys.argv[1]) as ts:
    EventInformationSection._table_ids = range(0x50, 0x70)
    for eit in ts.sections(EventInformationSection):
        for event in eit.events:
            for genre in event.descriptors.get(ContentDescriptor, []):
                nibble = genre.nibbles[0]
                # ジャンルがアニメでないイベント、アニメであっても放送開始時刻が5時から21時のものを除きます
                if nibble.content_nibble_level_1 != 0x07 or 4 < event.start_time.hour < 22:
                    continue
                for sed in event.descriptors.get(ShortEventDescriptor, []):
                    print(eit.service_id, event.event_id, event.start_time,
                          event.duration, sed.event_name_char, sed.text_char)
```
