#! /usr/bin/env python3

"""Problem の実装ファイル
:file: problem.py
:author: Yusuke Matsunaga (松永 裕介)

Copyright (C) 2019, 2020 Yusuke Matsunaga
All rights reserved.
"""

from core.position import Position
from core.block import Block
import sys


def print_block(block, fout):
    """ブロックを出力する．
    :param Block block: 対象のブロック
    :param FILE fout: 出力先のファイルオブジェクト
    """
    w = block.width
    h = block.height
    fout.write(f'BLOCK#{block.block_id} {w}X{h}\n')
    for y in range(h):
        first = True
        for x in range(w):
            if first:
                first = False
            else:
                fout.write(',')
            pos = Position(x, y)
            label = block.label(pos)
            if label == -1:  # 範囲外
                fout.write(' 0')
            elif label == 0:  # 範囲内だけどラベルなし
                fout.write(' +')
            else:
                fout.write(f'{label:2d}')
        fout.write('\n')


class Problem:
    """ADC2019の問題を表すクラス
    :param int width: 最大幅
    :param int height: 最大高さ
    """

    def __init__(self, width, height):
        self.set_size(width, height)

    def set_size(self, width, height):
        """サイズを(再)設定する．
        :param int width: 最大幅
        :param int height: 最大高さ
        以前の内容は消去される．
        """
        self.__max_width = width
        self.__max_height = height
        self.__block_list = []
        self.__terminals_dict = {}

    def add_block(self, block_id, pos_list, label_dict):
        """ブロックを追加する．
        :param int block_id: ブロック番号
        :param list[Pos] pos_list: ブロックの占める位置のリスト
        :param dict label_dict: ブロック上のラベル値の辞書．キーは位置
        - label_dict はラベルを持たない位置の値として0を持つ．
        - label_dict はブロックの領域外の位置の値は持たない．
        """
        self.__block_list.append(Block(block_id, pos_list, label_dict))
        for pos, label in label_dict.items():
            if label > 0:
                if label not in self.__terminals_dict:
                    self.__terminals_dict[label] = []
                self.__terminals_dict[label].append((block_id, pos))

    def is_valid(self):
        """内容が設定されていたら True を返す．"""
        return self.max_width > 0

    @property
    def max_width(self):
        """最大幅を返す．"""
        return self.__max_width

    @property
    def max_height(self):
        """最大高さを返す．"""
        return self.__max_height

    @property
    def block_num(self):
        """ブロック数を返す．"""
        return len(self.__block_list)

    @property
    def block_id_list(self):
        """ブロック番号のリストを返す．
        正確にはブロックリストのジェネレーターを返す．
        """
        for block in self.__block_list:
            yield block.block_id

    @property
    def block_list(self):
        """ブロックのリストを返す．
        正確にはブロックリストのジェネレーターを返す．
        """
        for block in self.__block_list:
            yield block

    def block(self, block_id):
        """ブロックを取り出す．
        :param int block_id: ブロック番号
        """
        assert 0 < block_id <= self.block_num
        block = self.__block_list[block_id - 1]
        assert block.block_id == block_id
        return block

    @property
    def line_id_list(self):
        """線分番号のリストを返す．
        正確にはジェネレーターを返す．
        """
        for line_id in sorted(self.__terminals_dict.keys()):
            yield line_id

    def terminals(self, line_id):
        """端子の情報を返す．
        :param int line_id: 線分番号
        :return: (block_id, pos) のリスト(要素数は常に2)を返す．
        """
        return self.__terminals_dict[line_id]

    def print(self, *, fout=sys.stdout):
        """内容を出力する．
        :param FILE fout: 出力先のファイルオブジェクト(キーワード引数)
        """
        fout.write('SIZE {}X{}\n'.format(self.max_width, self.max_height))
        fout.write('BLOCK_NUM {}\n'.format(self.block_num))
        for block in self.block_list:
            print_block(block, fout)
