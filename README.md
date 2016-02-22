# ariblib

ARIB-STD-B10 や ARIB-STD-B24 などの Python3+ での実装です。

m2tsをパースするライブラリと、応用を行ういくつかのコマンドからなります。

## インストール
このブランチのコードはまだ pip からはインストールできません

## コマンド利用例
### SRT 形式の字幕ファイルを作成する
```
$ python -m ariblib section --caption SRC DST
```
とすると、 SRC にある ts ファイルを読みこみ、字幕を DST に出力します。


### 現在の番組情報を取得する

```
$ python -m ariblib section --present SRC DST
```
とすると、 SRC にある ts ファイルを読みこみ、現在放送中の番組情報を DST に出力します。
