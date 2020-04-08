#! /usr/bin/env python3

### @file position.py
### @brief Position の実装ファイル
### @author Yusuke Matsunaga (松永 裕介)
###
### Copyright (C) 2019, 2020 Yusuke Matsunaga
### All rights reserved.


### @brief 位置を表すクラス
###
### 内容はただの (x, y) のタプル
### ただし +/- や +=/-= の演算を定義している．
### また，メンバ変数は初期化時に設定された
### 後は+=/-=演算以外では変更されない．
class Position :

    ### @brief 初期化
    ### @param[in] x, y 座標
    def __init__(self, x = 0, y = 0) :
        self.__x = x
        self.__y = y

    ### @brief 複製する．
    def copy(self) :
        return Position(self.x, self.y)

    ### @brief X座標を返す．
    @property
    def x(self) :
        return self.__x

    ### @brief Y座標を返す．
    @property
    def y(self) :
        return self.__y

    ### @brief 範囲内のときに True を返す．
    ### @param[in] width 幅
    ### @param[in] height 高さ
    def is_in_range(self, width, height) :
        if 0 <= self.x < width and 0 <= self.y < height :
            return True
        else :
            return False

    ### @brief 隣の位置を返す．
    ### @param[in] dir 方向を表す文字列 ('n', 'e', 's', 'w')
    def adjacent_pos(self, dir) :
        if dir == 'n' :
            return Position(self.x, self.y - 1)
        elif dir == 'e' :
            return Position(self.x + 1, self.y)
        elif dir == 's' :
            return Position(self.x, self.y + 1)
        elif dir == 'w' :
            return Position(self.x - 1, self.y)
        else :
            assert False

    ### @brief 位置の加算を行う．
    def __add__(self, right) :
        return Position(self.x + right.x, self.y + right.y)

    ### @brief 加算付き代入
    def __iadd__(self, right) :
        self.__x += right.x
        self.__y += right.y
        return self

    ### @brief 位置の減算を行う．
    def __sub__(self, right) :
        return Position(self.x - right.x, self.y - right.y)

    ### @brief 減算付き代入
    def __isub__(self, right) :
        self.__x -= right.x
        self.__y -= right.y
        return self

    ### @brief 等価比較演算
    def __eq__(self, right) :
        return self.x == right.x and self.y == right.y

    ### @brief 小なり比較演算
    def __lt__(self, right) :
        if self.x < right.x :
            return True
        elif self.x == right.x and self.y < right.y :
            return True
        return False

    ### @brief 小なりイコール比較演算
    def __le__(self, right) :
        if self.x < right.x :
            return True
        elif self.x == right.x and self.y <= right.y :
            return True
        return False

    ### @brief ハッシュ関数
    def __hash__(self) :
        return self.x * 37 + self.y

    ### @brief str 演算
    def __str__(self) :
        return '({},{})'.format(self.x, self.y)
