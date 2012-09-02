#!/usr/bin/env python3.2

"""TSシンタックスの実装"""

from ariblib.mnemonics import case_table, mnemonic

class SyntaxDict(dict):

    """シンタックスを記述する辞書クラス

    責務:
    1: 宣言された順番に記述子を格納するリストを提供する
    2: ビット列表記クラスに開始位置付与クラスと変数名を与える
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
            mnemonics = self.mnemonics[:]
            value.start = lambda instance: sum(mnemonic.real_length(instance)
                                               for mnemonic in mnemonics)
            self.mnemonics.append(value)
        dict.__setitem__(self, key, value)

class SyntaxType(type):

    """シンタックスのメタクラス

    SyntaxDict が生成したサブ情報を各インスタンスに付与する
    see: PEP3115
    """

    @classmethod
    def __prepare__(cls, name, bases):
        return SyntaxDict()

    def __new__(cls, name, args, classdict):
        object = type.__new__(cls, name, args, classdict)
        object._mnemonics = classdict.mnemonics
        object._conditions = classdict.conditions
        return object

class Syntax(metaclass=SyntaxType):

    """シンタックスの親クラス"""

    def __init__(self, packet):
        self._packet = packet

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

    def get_names(self):
        """このシンタックスインスタンスでアクセスできる
        ビット列プロパティの一覧を返す"""

        result = []
        for mnemonic in self._mnemonics:
            name = mnemonic.name
            if isinstance(mnemonic, case_table):
                if mnemonic.condition(self):
                    result.extend(getattr(self, name).get_names())
            else:
                result.append(name)
        return result

