#!/usr/bin/env python3.2

from hashlib import md5

try:
    from PIL import Image
    from PIL.ImageDraw import Draw
except ImportError:
    text_output = True
else:
    text_output = False

import csv
import os.path

import ariblib

save_dir = os.path.expanduser('~/.ariblib/drcs/')
mapping_path = os.path.join((os.path.split(ariblib.__file__)[0]), 'drcs.tsv')
user_mapping_path = os.path.expanduser('~/.ariblib/drcs.tsv')
mapping = {}

# DRCSイメージ保存ディレクトリが存在しない場合は作成する
if not os.path.isdir(save_dir):
    import os
    os.makedirs(save_dir)

for path in (mapping_path, user_mapping_path):
    if os.path.isfile(path):
        with open(path) as f:
            reader = csv.reader(f, delimiter='\t')
            mapping.update(line for line in reader)

class DRCSImage(object):

    """DRCSの画像イメージ"""

    def __init__(self, width, height, bgcolor='white'):
        self.image = Image.new('RGB', (width, height), bgcolor)
        self.hash = None

    def point(self, patterns):
        hasher = md5()
        draw = Draw(self.image)
        for y, pattern in enumerate(patterns):
            pattern_data = pattern.pattern_data
            hasher.update(pattern_data)
            points = [(x, y) for x, dot in enumerate(_to_bit(pattern_data))
                             if dot == '1']
            draw.point(points, 'black')
        self.hash = hasher.hexdigest()

    def save(self, ext='png', path=None):
        if path is None:
            if self.hash is None:
                raise ValueError('画像イメージが作成されていません')
            path = self.hash
        self.image.save(os.path.join(save_dir, path + '.' + ext))

class DRCSText(object):

    """DRCSのテキストイメージ"""

    def __init__(self, width, height, bgcolor='white'):
        self.hash = None
        self.dots = []

    def point(self, patterns):
        hasher = md5()
        for pattern in patterns:
            pattern_data = pattern.pattern_data
            hasher.update(pattern_data)
            points = _to_bit(pattern_data).replace('0', '　').replace('1', '■')
            self.dots.append(points)
        self.hash = hasher.hexdigest()

    def save(self, ext='txt', path=None):
        if path is None:
            if self.hash is None:
                raise ValueError('画像イメージが作成されていません')
            path = self.hash
        with open(os.path.join(save_dir, path + '.' + ext), 'w') as out:
            out.write('\n'.join(self.dots))

def _to_bit(raw):
    """bytearrayを0,1のビットを表す文字列に変換する"""

    return ''.join(map(lambda s: format(s, '08b'), raw))

# 画像出力ができないときはテキスト出力を行う
if text_output:
    DRCSImage = DRCSText

