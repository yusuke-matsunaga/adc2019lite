#! /usr/bin/env python3

"""Position の実装ファイル
:file: position.py
:author: Yusuke Matsunaga (松永 裕介)

Copyright (C) 2019, 2020 Yusuke Matsunaga
All rights reserved.
"""


class Position:
    """位置を表すクラス
    内容はただの (x, y) のタプル
    ただし +/- や +=/-= の演算を定義している．
    また，メンバ変数は初期化時に設定された後は
    +=/-=演算以外では変更されない．

    :param int x, y: 座標
    """

    def __init__(self, x=0, y=0):
        self.__x = x
        self.__y = y

    def copy(self):
        """複製する．"""
        return Position(self.x, self.y)

    @property
    def x(self):
        """X座標を返す．"""
        return self.__x

    @property
    def y(self):
        """Y座標を返す．"""
        return self.__y

    def is_in_range(self, width, height):
        """範囲内のときに True を返す．
        :param int width: 幅
        :param int height: 高さ
        """
        if 0 <= self.x < width and 0 <= self.y < height:
            return True
        else:
            return False

    def adjacent_pos(self, dir):
        """隣の位置を返す．
        :param str dir: 方向を表す文字列 ('n', 'e', 's', 'w')
        """
        if dir == 'n':
            return Position(self.x, self.y - 1)
        elif dir == 'e':
            return Position(self.x + 1, self.y)
        elif dir == 's':
            return Position(self.x, self.y + 1)
        elif dir == 'w':
            return Position(self.x - 1, self.y)
        else:
            assert False

    def __add__(self, right):
        """位置の加算を行う．"""
        return Position(self.x + right.x, self.y + right.y)

    def __iadd__(self, right):
        """加算付き代入"""
        self.__x += right.x
        self.__y += right.y
        return self

    def __sub__(self, right):
        """位置の減算を行う．"""
        return Position(self.x - right.x, self.y - right.y)

    def __isub__(self, right):
        """減算付き代入"""
        self.__x -= right.x
        self.__y -= right.y
        return self

    def __eq__(self, right):
        """等価比較演算"""
        return self.x == right.x and self.y == right.y

    def __lt__(self, right):
        """小なり比較演算"""
        if self.x < right.x:
            return True
        elif self.x == right.x and self.y < right.y:
            return True
        return False

    def __le__(self, right):
        """小なりイコール比較演算"""
        if self.x < right.x:
            return True
        elif self.x == right.x and self.y <= right.y:
            return True
        return False

    def __hash__(self):
        """ハッシュ関数"""
        return self.x * 37 + self.y

    def __str__(self):
        """str 演算"""
        return f'({self.x},{self.y})'
