#! /usr/bin/env python3

"""Answer の実装ファイル

:file: answer.py
:author: Yusuke Matsunaga (松永 裕介)

Copyright (C) 2019, 2020 Yusuke Matsunaga
All rights reserved.
"""

from core.block import Block
from core.position import Position
import sys


class Answer:
    """ADC2019 の解答を表すクラス
    - 盤面のサイズ
    - 盤面のラベル(線分番号)
    - ブロックの位置座標を持つ．
    """

    def __init__(self, width, height):
        self.__width = width
        self.__height = height
        self.__label_array = [0 for i in range(width * height)]
        self.__block_pos_dict = {}

    @property
    def width(self):
        """幅を返す．"""
        return self.__width

    @property
    def height(self):
        """高さを返す．"""
        return self.__height

    def label(self, *args):
        """ラベルを返す．
        引数は以下のいずれか
        - Position
        - int, int
        どちらも対象の位置座標を表す．
        """
        if len(args) == 1 and isinstance(args[0], Position):
            pos = args[0]
        elif len(args) == 2 \
             and isinstance(args[0], int) \
             and isinstance(args[1], int):
            pos = Position(args[0], args[1])
        else:
            print('Error in Ansswer.label(args):  args must be Position or (int, int)')
            assert False
        index = self.__pos_to_index(pos)
        return self.__label_array[index]

    def block_pos(self, block_id):
        """ブロックの位置を返す．
        :param int block_id: ブロック番号
        """
        assert block_id in self.__block_pos_dict
        return self.__block_pos_dict[block_id]

    def set_label(self, pos, label):
        """ラベルを設定する．
        :param Position pos: 位置
        :param int label: ラベル
        """
        index = self.__pos_to_index(pos)
        self.__label_array[index] = label

    def set_block_pos(self, block_id, pos):
        """ブロックの位置を設定する．
        :param int block_id: ブロック番号
        :param Position pos: 位置
        """
        self.__check_pos(pos)
        self.__block_pos_dict[block_id] = pos

    def print(self, *, fout=sys.stdout):
        """内容を出力する．
        :param FILE fout: 出力先のファイルオブジェクト(キーワード引数)
        """
        fout.write(f'SIZE {self.width}X{self.height}\n')
        for y in range(self.height):
            for x in range(self.width):
                if x > 0:
                    fout.write(',')
                label = self.label(Position(x, y))
                fout.write(f'{label:2d}')
            fout.write('\n')
        for block_id in sorted(self.__block_pos_dict.keys()):
            pos = self.block_pos(block_id)
            fout.write(f'BLOCK#{block_id} @{pos}\n')

    def __pos_to_index(self, pos):
        """pos をラベル配列のインデックスに変換する．
        :param Position pos: 位置
        """
        x = pos.x
        y = pos.y
        assert 0 <= x and x < self.width
        assert 0 <= y and y < self.height
        return y * self.__width + x

    def __check_pos(self, pos):
        """pos が範囲内かチェックする．
        :param Position pos: 位置
        """
        x = pos.x
        y = pos.y
        assert 0 <= x and x < self.width
        assert 0 <= y and y < self.height


if __name__ == '__main__':

    ans = Answer(5, 5)

    ans.set_label(Position(3, 3), 1)

    ans.set_block_pos(1, Position(2, 2))

    ans.print()
