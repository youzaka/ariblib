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


### tsから必要なストリームのみを取り出す(ワンセグなどの削除)
```
$ python -m ariblib split SRC DST
```
とすると、 SRC にある ts ファイルが指定する PAT 情報を読み込み、最初のストリームの動画・音声のみを保存した TS ファイルを DST に保存します。 TSSplitter のようなことができます。

