#! /usr/bin/env python3

## @file satbool3.py
# @brief 3値のブール値を表すクラス
# @author Yusuke Matsunaga (松永 裕介)
#
# Copyright (C) 2017 Yusuke Matsunaga
# All rights reserved.


from enum import Enum


## @brief SAT の結果を表す列挙型
#
# 真(B3True)，偽(B3False) の他に不定値を表す B3X
# がある．
class SatBool3(Enum) :
    X     =  0
    TRUE  =  1
    FALSE = -1


    ## @brief 否定を返す．
    def negate(self) :
        if self == SatBool3.X :
            return SatBool3.X
        elif self == SatBool3.TRUE :
            return SatBool3.FALSE
        elif self == SatBool3.FALSE :
            return SatBool3.TRUE
        else :
            assert False

    ## @brief 文字列表現を返す．
    def __repr__(self) :
        if self == SatBool3.X :
            return 'X(unknown)'
        elif self == SatBool3.TRUE :
            return 'True'
        elif self == SatBool3.FALSE :
            return 'False'
        else :
            assert False
