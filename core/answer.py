#! /usr/bin/env python3

### @file answer.py
### @brief Answer の実装ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2019, 2020 Yusuke Matsunaga
### All rights reserved.

from core.block import Block
from core.position import Position
import sys


### @brief ADC2019 の解答を表すクラス
###
### - 盤面のサイズ
### - 盤面のラベル(線分番号)
### - ブロックの位置座標
### を持つ．
class Answer :

    ### @brief 初期化
    def __init__(self, width, height) :
        self.__width = width
        self.__height = height
        self.__label_array = [ 0 for i in range(width * height) ]
        self.__block_pos_dict = dict()

    ### @brief 幅を返す．
    @property
    def width(self) :
        return self.__width

    ### @brief 高さを返す．
    @property
    def height(self) :
        return self.__height

    ### @brief ラベルを返す．
    ###
    ### 引数は以下のいずれか
    ### - Position
    ### - int, int
    ### どちらも対象の位置座標を表す．
    def label(self, *args) :
        if len(args) == 1 and isinstance(args[0], Position) :
            pos = args[0]
        elif len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], int) :
            pos = Position(args[0], args[1])
        else :
            print('Error in Ansswer.label(args):  args must be Position or (int, int)')
            assert False
        index = self.__pos_to_index(pos)
        return self.__label_array[index]

    ### @brief ブロックの位置を返す．
    def block_pos(self, block_id) :
        assert block_id in self.__block_pos_dict
        return self.__block_pos_dict[block_id]

    ### @brief ラベルを設定する．
    def set_label(self, pos, label) :
        index = self.__pos_to_index(pos)
        self.__label_array[index] = label

    ### @brief ブロックの位置を設定する．
    def set_block_pos(self, block_id, pos) :
        self.__check_pos(pos)
        self.__block_pos_dict[block_id] = pos

    ### @brief 内容を出力する．
    ### @param[in] fout 出力先のファイルオブジェクト(キーワード引数)
    def print(self, *, fout = sys.stdout) :
        fout.write('SIZE {}X{}\n'.format(self.width, self.height))
        for y in range(self.height) :
            for x in range(self.width) :
                if x > 0 :
                    fout.write(',')
                fout.write('{:2d}'.format(self.label(Position(x, y))))
            fout.write('\n')
        for block_id in sorted(self.__block_pos_dict.keys()) :
            pos = self.block_pos(block_id)
            fout.write('BLOCK#{} @{}\n'.format(block_id, pos))

    ### @brief pos をラベル配列のインデックスに変換する．
    def __pos_to_index(self, pos) :
        x = pos.x
        y = pos.y
        assert 0 <= x and x < self.width
        assert 0 <= y and y < self.height
        return y * self.__width + x

    ### @brief pos が範囲内かチェックする．
    def __check_pos(self, pos) :
        x = pos.x
        y = pos.y
        assert 0 <= x and x < self.width
        assert 0 <= y and y < self.height


if __name__ == '__main__' :

    ans = Answer(5, 5)

    ans.set_label(Position(3, 3), 1)

    ans.set_block_pos(1, Position(2, 2))

    ans.print()
