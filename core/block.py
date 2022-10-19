#! /usr/bin/env python3

"""Block の実装ファイル
:file:block.py
:author: Yusuke Matsunaga (松永 裕介)

Copyright (C) 2019, 2020 Yusuke Matsunaga
All rights reserved.
"""

import sys
from core.position import Position


def block_type(pat):
    """ブロックの形状を調べる．"""
    I_pat_list = [[Position(0, 0),
                   Position(0, 1),
                   Position(0, 2),
                   Position(0, 3)],
                  [Position(0, 0),
                   Position(1, 0),
                   Position(2, 0),
                   Position(3, 0)]]
    O_pat_list = [[Position(0, 0),
                   Position(1, 0),
                   Position(0, 1),
                   Position(1, 1)]]
    T_pat_list = [[Position(1, 0),
                   Position(0, 1),
                   Position(1, 1),
                   Position(2, 1)],
                  [Position(1, 0),
                   Position(0, 1),
                   Position(1, 1),
                   Position(1, 2)],
                  [Position(0, 0),
                   Position(1, 0),
                   Position(2, 0),
                   Position(1, 1)],
                  [Position(0, 0),
                   Position(0, 1),
                   Position(1, 1),
                   Position(0, 2)]]
    J_pat_list = [[Position(1, 0),
                   Position(1, 1),
                   Position(0, 2),
                   Position(1, 2)],
                  [Position(0, 0),
                   Position(0, 1),
                   Position(1, 1),
                   Position(2, 1)],
                  [Position(0, 0),
                   Position(1, 0),
                   Position(0, 1),
                   Position(0, 2)],
                  [Position(0, 0),
                   Position(1, 0),
                   Position(2, 0),
                   Position(2, 1)]]
    L_pat_list = [[Position(0, 0),
                   Position(0, 1),
                   Position(0, 2),
                   Position(1, 2)],
                  [Position(0, 0),
                   Position(1, 0),
                   Position(2, 0),
                   Position(0, 1)],
                  [Position(0, 0),
                   Position(1, 0),
                   Position(1, 1),
                   Position(1, 2)],
                  [Position(2, 0),
                   Position(0, 1),
                   Position(1, 1),
                   Position(2, 1)]]
    S_pat_list = [[Position(1, 0),
                   Position(2, 0),
                   Position(0, 1),
                   Position(1, 1)],
                  [Position(0, 0),
                   Position(0, 1),
                   Position(1, 1),
                   Position(1, 2)]]
    Z_pat_list = [[Position(0, 0),
                   Position(1, 0),
                   Position(1, 1),
                   Position(2, 1)],
                  [Position(1, 0),
                   Position(0, 1),
                   Position(1, 1),
                   Position(0, 2)]]

    for I_pat in I_pat_list:
        if pat == I_pat:
            return 'I'
    for O_pat in O_pat_list:
        if pat == O_pat:
            return 'O'
    for T_pat in T_pat_list:
        if pat == T_pat:
            return 'T'
    for J_pat in J_pat_list:
        if pat == J_pat:
            return 'J'
    for L_pat in L_pat_list:
        if pat == L_pat:
            return 'L'
    for S_pat in S_pat_list:
        if pat == S_pat:
            return 'S'
    for Z_pat in Z_pat_list:
        if pat == Z_pat:
            return 'Z'
    return 'X'


class Block:
    """ブロックを表すクラス

    :param int block_id: ブロック番号
    :param list[Position] pos_list: ブロックの占める位置のリスト
    :param dict label_dict: ブロック上のラベル値の辞書．キーは位置
    - label_dict はラベルを持たない位置の値として0を持つ．
    - label_dict はブロックの領域外の位置の値は持たない．
    """
    def __init__(self, block_id, pos_list, label_dict):
        self.__block_id = block_id
        self.__pos_list = list(pos_list)
        self.__label_dict = dict(label_dict)

        # 幅と高さを求める．
        x_max = 0
        y_max = 0
        for pos in self.__pos_list:
            x = pos.x
            if x_max < x:
                x_max = x
            y = pos.y
            if y_max < y:
                y_max = y
        w = x_max + 1
        h = y_max + 1
        self.__width = w
        self.__height = h

        # ブロックの種類を調べる．
        self.__type = block_type(self.__pos_list)

    @property
    def block_id(self):
        """ブロック番号を返す．"""
        return self.__block_id

    @property
    def pos_list(self):
        """ブロックの占めている位置のリストを返す．
        - ブロックの左上隅の座標を (0, 0) とする．
        - 正確にはジェネレータを返す．
        """
        for pos in self.__pos_list:
            yield pos

    def label(self, pos):
        """指定された位置のラベルを返す．
        :param Position pos: 対象の位置
        :return: ラベル値
        - ラベルがない場合は 0 を返す．
        - 位置が間違っている場合は -1 を返す．
        """
        if pos in self.__label_dict:
            return self.__label_dict[pos]
        else:
            return -1

    @property
    def pos_label_list(self):
        """位置とラベルのリストを返す．
        - 正確にはジェネレータを返す．
        - ラベルを持たない位置は含まない．
        """
        for pos, label in self.__label_dict.items():
            if label > 0:
                yield pos, label

    @property
    def width(self):
        """幅を返す．"""
        return self.__width

    @property
    def height(self):
        """高さを返す．"""
        return self.__height

    @property
    def type(self):
        """ブロックの種類を返す．"""
        return self.__type
