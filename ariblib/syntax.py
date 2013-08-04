#!/usr/bin/env python3.2

"""TSシンタックスの実装"""

from ariblib.mnemonics import case_table, mnemonic

class SyntaxDict(dict):

    """シンタックスを記述する辞書クラス

    責務:
    1: 宣言された順番に記述子を格納するリストを提供する
    2: ビット列表記クラスに開始位置と変数名を与える
    3: ifセクション解決用のリストを提供する
    """

    def __init__(self):
        self.mnemonics = []
        self.conditions = []

    def __setitem__(self, key, value):
        if isinstance(value, case_table):
            self.conditions.append(value)

        if isinstance(value, mnemonic):
            value.name = key
            value.start = self.get_start()
            self.mnemonics.append(value)

        dict.__setitem__(self, key, value)

    def get_start(self):
        mnemonics = self.mnemonics[:]
        def start(instance):
            return sum(m.real_length(instance) for m in mnemonics) + instance._pos
        return start

class SyntaxType(type):

    """シンタックスのメタクラス

    SyntaxDict が生成したサブ情報を各インスタンスに付与する
    see: PEP3115
    """

    @classmethod
    def __prepare__(cls, name, bases):
        return SyntaxDict()

    def __new__(cls, name, args, classdict):
        instance = type.__new__(cls, name, args, classdict)
        instance._mnemonics = classdict.mnemonics
        instance._conditions = classdict.conditions
        return instance

class Syntax(metaclass=SyntaxType):

    """シンタックスの親クラス"""

    def __init__(self, packet, pos=0, parent=None):
        self._packet = packet
        self._pos = pos
        self._parent = parent
        self._callbacks = dict()

    def __len__(self):
        """このシンタックスが持っているビット列表記の長さを全て数え上げ、
        シンタックスの長さをバイト数として返す"""

        return sum(mnemonic.real_length(self) for mnemonic in self._mnemonics)

    def __getattr__(self, name):
        """指定されたプロパティが直下から見つからない場合に、
        条件に合うifシンタックスを順番に探していく"""

        for mnemonic in self._conditions:
            try:
                if mnemonic.condition(self):
                    sub = getattr(self, mnemonic.name)
                    return getattr(sub, name)
            except AttributeError:
                pass

        # 親が与えられている場合は親のプロパティも参照する
        if (self._parent and
            any(mnemonic.name == name for mnemonic in self._parent._mnemonics)):
            return getattr(self._parent, name)

    def get_names(self):
        """このシンタックスインスタンスでアクセスできる
        ビット列プロパティの一覧を返す"""

        result = []
        for mnemonic in self._mnemonics:
            name = mnemonic.name
            if isinstance(mnemonic, case_table):
                if mnemonic.condition(self):
                    result.extend(mnemonic.cls(self).get_names())
            else:
                result.append(name)
        return result

    def dump(self, indent=0):
        from ariblib.aribstr import AribString
        from ariblib.sections import Section
        from ariblib.descriptors import Descriptor
        from types import GeneratorType
        from collections import defaultdict
        print('{}{}'.format(' ' * indent, '-' * (80 - indent)))
        if isinstance(self, Section) or isinstance(self, Descriptor):
            print('{}<<{}>>'.format(' ' * indent, self.__class__.__name__))
        for name in self.get_names():
            value = getattr(self, name)
            if isinstance(value, Syntax):
                value.dump(indent + 2)
            elif isinstance(value, defaultdict):
                for value in value.values():
                    for child in value:
                        child.dump(indent + 2)
            elif isinstance(value, list):
                for child in value:
                    child.dump(indent + 2)
            elif type(value) is GeneratorType:
                for child in value:
                    child.dump(indent + 2)
            elif isinstance(value, bytearray):
                print("{}{}\t{}".format(' ' * indent, name, AribString(value)))
            else:
                print("{}{}\t{}".format(' ' * indent, name, value))

    def on(self, Descriptor, descriptor_name='descriptors'):
        """記述子ごとにコールバック関数を設定する
        いまのところ、一つの記述子についてコールバック関数は1つのみ定義できる。
        """

        self.descriptor_name = descriptor_name
        def attach_callback(callback):
            self._callbacks[Descriptor] = callback
        return attach_callback

    def execute(self):
        """指定された記述子がyieldされるごとにコールバック関数を実行する"""
        from ariblib.descriptors import ExtendedEventDescriptor

        for descriptor_type, descriptors in getattr(self, self.descriptor_name).items():
            if descriptor_type not in self._callbacks:
                continue

            callback = self._callbacks[descriptor_type]
            if descriptor_type == ExtendedEventDescriptor:
                # 拡張形式イベント記述子の場合は別途対応が必要。TODO
                callback(descriptors)
            else:
                for descriptor in descriptors:
                    callback(descriptor)

