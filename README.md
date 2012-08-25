ariblib
=======

速度優先の Transport Stream パーサです。

テーブルなどをいちいち class として実装すると遅くなるので、モジュール下に直接関数としていろいろ実装しています。
そのため、 ```section.start_time()``` でなく ```eit.start_time(section)``` とかく必要があったりして見た目があんまり良くないです。
テーブルレイヤ・記述子レイヤについては class にしても速度があんまり遅くならないように書き換えたいとは思っています。
とりあえず字幕と EPG だけ出せるようにしています。

使い方例1 字幕を表示
```python

import sys

from ariblib import TransportStreamFile, caption

with TransportStreamFile(sys.argv[1]) as ts:
    for table in caption.tables(ts):
        for section in caption.sections(table):
            if caption.data_unit_parameter(section) == 0x20:
                body = caption.CProfileString(caption.data_unit_data(section))
                print(body)
```
古い実装であった色わけとかもそのうち実装し直します

使い方例2 番組表を表示
```python

import sys
from collections import defaultdict
from ariblib import TransportStreamFile, eit

with TransportStreamFile(sys.argv[1]) as ts:
    for table in eit.tables(ts):
        for section in eit.sections(table):
            print(eit.start_time(section), eit.duration(section))
            longdesc = defaultdict(bytearray)
            for descriptor in eit.descriptors(section):
                if descriptor[0] == 0x4D:
                    event_name_length = descriptor[5]
                    event_name_char = AribString(descriptor[6:6+event_name_length])
                    text_length = descriptor[6+event_name_length]
                    text_char = AribString(
                        descriptor[7+event_name_length:7+event_name_length+text_length])
                    print(event_name_char, text_char)
                if descriptor[0] == 0x4E:
                    length_of_items = descriptor[6]
                    index = 7
                    desc_last = 6 + length_of_items
                    while index < desc_last:
                        item_description_length = descriptor[index]
                        item_description_char = AribString(descriptor[index+1:
                                                           index+1+item_description_length])
                        item_length = descriptor[index+1+item_description_length]
                        item_char = descriptor[index+2+item_description_length:
                                               index+2+item_description_length+item_length]
                        longdesc[item_description_char].extend(item_char)
                        index += 2 + item_description_length + item_length
            for key, value in longdesc.items():
                print(key, AribString(value))
```

記述子のパースの仕方がださいので、テーブルも含めてイベントドリブンな感じで書けるようにできたらいいなあと思ってます。



